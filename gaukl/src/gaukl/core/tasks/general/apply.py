import logging
from pathlib import Path
from typing import Tuple

from gaukl.core.context.context import Context
from gaukl.core.workflow import load_yaml_tpl, build_workflow, execute_workflow
from gaukl.core.tasks.task import task, Roles
from gaukl.core.helper.files import load_yaml_path


def match_rules(context: Context, rules: list) -> bool:
    logger = logging.getLogger('match rules')

    # Build a workflow of the rules and execute it
    rules_workflow = build_workflow(rules, context['environment']['tasks'])
    try:
        execute_workflow(context, rules_workflow)
        matched = True
        logger.debug(f'Rules matched for {rules_workflow}')
    # If any of the rules throws an exception, the ruleset is marked as not matched
    # TODO: throw notmatched-exception and only catch that
    except Exception:
        matched = False

    return matched


def apply_manipulations(context: Context, manipulations: list, response: str) -> Context:
    # Load the response and expand the template
    response = load_yaml_tpl(context['environment']['config']['paths']['responses_path'], response, context)
    # Set the headers and body
    context.parsed_response_header(response['header'])
    context['response']['body']['parsed'] = response['body']
    # If we have manipulations to apply, build a workflow of the manipulations and execute it
    if manipulations is not None and len(manipulations) > 0:
        manipulations_workflow = build_workflow(manipulations, context['environment']['tasks'])
        context = execute_workflow(context, manipulations_workflow)
    return context


def apply_ruleset(context: Context, ruleset_file: Path) -> Tuple[bool, dict]:
    # Load ruleset
    ruleset = load_yaml_path(ruleset_file)
    rules = ruleset['if'] or []

    # Try to match all rules if there are any, else match is always True
    if len(rules) > 0:
        matched = match_rules(context, rules)
    else:
        matched = True

    return matched, ruleset


@task(shortname='apply_ruleset', role=Roles.WORKFLOW, async=False)
def apply(context: Context) -> Context:
    """Applies a ruleset
    If there is a match we set context['is_matched'] = True
    This can be used in further tasks like proxy
    """
    full_path_ruleset_files = [
        Path(context['environment']['config']['paths']['rulesets_path']).joinpath(ruleset_file)
        for ruleset_file in context['environment']['recipe']['rulesets']
    ]
    for full_path_ruleset_file in full_path_ruleset_files:
        matched, ruleset = apply_ruleset(context, full_path_ruleset_file)
        # If the rules in the ruleset where matched, apply manipulations and return
        if matched:
            context.is_matched(True)
            return apply_manipulations(context, ruleset['with'] or [], ruleset['use'])
    return context
