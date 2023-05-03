#!/bin/bash
#SBATCH --job-name run_semanticParserShort
#SBATCH --time=16:00:00
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --account=PAS2271

module load python/3.7-2019.10 cuda
echo "Loaded modules"
cd /users/PAS1372/osu10106/projects/foodshed/semantic_parsing_with_constrained_lm/
echo "Entered directory"
source $HOME/.poetry/env
echo "Sourced poetry"
bash runOvernight.sh