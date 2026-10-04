# Stage scripts

These scripts delegate to the installed `structsynth` CLI. Install the package
from the project root before running them:

```bash
python -m pip install -e '.[evaluation]'
```

| Script | Equivalent command | Stage |
|---|---|---|
| `run_data_split.py` | `structsynth split` | Prepare the training, test and prompt-example data |
| `run_structure_learning.py` | `structsynth discover` | Induce the dependency graph |
| `run_data_generation.py` | `structsynth generate` | Generate synthetic rows from the graph |

Run stages in order from the project root, using `--resume` to reuse the preceding
stage's artifacts:

```bash
python scripts/run_data_split.py --config configs/adult.yaml --seeds 42
python scripts/run_structure_learning.py --config configs/adult.yaml --seeds 42 --resume
python scripts/run_data_generation.py --config configs/adult.yaml --seeds 42 --resume
structsynth evaluate --config configs/adult.yaml --seeds 42 --resume
```

Splitting is local. Discovery and generation use the configured model endpoint
and credentials unless `--replay-dir` supplies recorded responses. Use `--help`
on any script to inspect the available arguments.

Paths inside the YAML configuration resolve relative to the configuration file.
From another working directory, pass the script and configuration paths explicitly.
The three scripts are also included in the source distribution; wheel installs
provide the equivalent `structsynth` commands.

For the complete pipeline, use `structsynth run --config configs/adult.yaml`.
For a complete offline example, use `structsynth demo --output-dir runs/demo`.
