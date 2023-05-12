export PRETRAINED_MODEL_DIR=facebook/bart-large
export TRAINED_MODEL_DIR=trained_models/


QUERY=$1

python -m semantic_parsing_with_constrained_lm.run_instant \
--config-name semantic_parsing_with_constrained_lm.configs.liveRun \
--log-dir logs/ \
--model Bart \
--utterance "$QUERY" \
--exp-name-pattern 'overnight_Bart_test-full_.*_constrained_canonicalUtterance_train-200' 