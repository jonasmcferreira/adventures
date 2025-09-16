# novelgen

novelgen is a modular AWS Bedrock pipeline for producing long-form fiction artifacts. It orchestrates a structured workflow that turns a high-level brief into a complete outline, sample scenes, and an evolving story bible.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure AWS credentials that grant access to the selected Bedrock model and make sure the profile referenced in `config.yaml` is available.

## Configuration

The global configuration lives in `config.yaml`. It defines the AWS region, credential profile, model ID, and generation parameters, as well as the output directory. Edit the file before running the pipeline or override individual values with CLI options where available.

```yaml
region: eu-west-3
profile: default
model_id: anthropic.claude-3-5-sonnet-20240620-v1:0
temperature: 0.7
max_tokens: 2048
out_dir: ./output
```

## Example commands

Generate only the premise from constraint flags:

```bash
python -m novelgen.cli premise --genre Fantasy --setting "Iberia 150 BCE" --hook "Rome vs druidic gods"
```

Run the entire pipeline producing scene cards for the first two chapters:

```bash
python -m novelgen.cli run_all --genre Fantasy --setting "Iberia 150 BCE" --hook "Rome vs druidic gods" --cards 2
```

List available commands:

```bash
python -m novelgen.cli --help
```

The pipeline writes all artifacts to `./output` following the deterministic layout described in the project spec. See the CLI help for module-level commands.
