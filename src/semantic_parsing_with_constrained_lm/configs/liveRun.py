# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from typing import Callable, Dict, Tuple

import torch
from typing_extensions import Literal

from semantic_parsing_with_constrained_lm.configs.lib.common import make_semantic_parser
from semantic_parsing_with_constrained_lm.datum import Datum
from semantic_parsing_with_constrained_lm.domains.overnight import OutputType, OvernightPieces
from semantic_parsing_with_constrained_lm.eval import TopKExactMatch
from semantic_parsing_with_constrained_lm.lm import TRAINED_MODEL_DIR, AutoregressiveModel, ClientType
from semantic_parsing_with_constrained_lm.lm_bart import Seq2SeqBart
from semantic_parsing_with_constrained_lm.lm_openai_gpt3 import IncrementalOpenAIGPT3
from semantic_parsing_with_constrained_lm.paths import DOMAINS_DIR
from semantic_parsing_with_constrained_lm.run_instant import EvalSplit, Experiment
from semantic_parsing_with_constrained_lm.search import PartialParse, StartsWithSpacePartialParse

from pdb import set_trace as bp
from semantic_parsing_with_constrained_lm.async_tools import limits

def build_config(_log_dir, **_kwargs,) -> Dict[str, Callable[[], Experiment]]:
    BEAM_SIZE = 10

    model = _kwargs["model"]
    use_gpt3 = model == ClientType.GPT3

    all_pieces: Dict[Tuple[str, OutputType], OvernightPieces] = {}
    max_steps_by_config: Dict[Tuple[str, OutputType], int] = {}

    def create_exp(
        problem_type: Literal[
            "constrained", "unconstrained-beam", "unconstrained-greedy"
        ],
        output_type: OutputType,
        domain: str,
        train_size: int,
    ):
        lm: AutoregressiveModel
        # lm = Seq2SeqBart(
        #     f"{TRAINED_MODEL_DIR}/20000/overnight_{domain}_{output_type}/",
        #     device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu"),
        # )

        lm = Seq2SeqBart(
            "trained_models/foodshed_utterance/",
            device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        )


        # lm.predict()
        pieces = all_pieces.get((domain, output_type))
        if not pieces:
            pieces = all_pieces[domain, output_type] = OvernightPieces.from_dir(
                lm.tokenizer,
                DOMAINS_DIR / "overnight/data",
                domain,
                is_dev=False,
                k=BEAM_SIZE,
                output_type=output_type,
                simplify_logical_forms=True,
                # TODO: Set prefix_with_space properly by inspecting `lm`
                prefix_with_space=True,
            )
        max_steps = max_steps_by_config.get((domain, output_type))
        if max_steps is None:
            max_steps = max_steps_by_config[domain, output_type] = (
                max(
                    len(lm.tokenizer.tokenize(" " + canon))
                    for canon in pieces.denotation_metric.canonical_to_denotation
                )
                + 3  # +3 to be safe
            )

        train_data = pieces.train_data[:train_size]
        # if eval_split == EvalSplit.TrainSubset:
        #     test_data = pieces.train_data[-100:]
        # elif eval_split in (EvalSplit.TestFull, EvalSplit.DevFull):
        #     test_data = pieces.test_data
        # elif eval_split in (EvalSplit.TestSubset, EvalSplit.DevSubset):
        #     test_data = pieces.test_data[:100]

        partial_parse_builder: Callable[[Datum], PartialParse]
        if problem_type == "constrained":
            partial_parse_builder = pieces.partial_parse_builder  # type: ignore
            beam_size = BEAM_SIZE
        elif problem_type.startswith("unconstrained"):
            partial_parse = StartsWithSpacePartialParse(lm.tokenizer)
            partial_parse_builder = lambda _: partial_parse
            if problem_type == "unconstrained-beam":
                beam_size = BEAM_SIZE
            elif problem_type == "unconstrained-greedy":
                beam_size = 1
            else:
                raise ValueError(problem_type)
        else:
            raise ValueError(f"{problem_type} not allowed")

        testDatum = Datum(None, None, None, _kwargs['utterance'])
        test_data = [testDatum]

        parser = make_semantic_parser(
            train_data,
            lm,
            use_gpt3,
            max_steps,
            beam_size,
            partial_parse_builder,
            lambda _datum: max_steps,
        )

        '''AMAD: Need to make a parser'''
        return Experiment(
            model=parser,
            client=lm,
            metrics={
                "exact_match": TopKExactMatch(beam_size),
                "denotation": pieces.denotation_metric,
            },
            test_data=test_data,
        )

    def add_exp_to_dict(
        exps_dict: Dict[str, Callable[[], Experiment]],
        problem_type: Literal[
            "constrained", "unconstrained-beam", "unconstrained-greedy"
        ],
        output_type: OutputType,
        domain: str,
        train_size: int,
    ):
        # exp_name = f"overnight_{model}_{eval_split}_{domain}_{problem_type}_{output_type}_train-{train_size}"
        exp_name = f"overnight_{model}_test-full_{domain}_{problem_type}_canonicalUtterance_train-{train_size}"
        exps_dict[exp_name] = lambda: create_exp(
            problem_type, output_type, domain, train_size
        )

    domain = "foodshed"
    result: Dict[str, Callable[[], Experiment]] = {}
    add_exp_to_dict(result, "constrained", OutputType.Utterance, domain, 200)
    return result
