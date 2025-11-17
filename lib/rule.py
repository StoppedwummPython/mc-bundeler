import platform
import sys

# Determine the current operating system and map it to the expected names.
# platform.system() returns 'Windows', 'Linux', or 'Darwin' for macOS.
_current_os_name = {
    "windows": "windows",
    "linux": "linux",
    "darwin": "osx",
}.get(sys.platform.lower(), "unknown")

# Determine the architecture, mapping common outputs to the expected 'x86'.
# Note: This simple check assumes anything not '64' is '32'/'x86'.
_is_64_bit = sys.maxsize > 2**32
_current_os_arch = "x64" if _is_64_bit else "x86"


def is_rule_applicable(ruleset: dict) -> bool:
    """
    Parses a dictionary containing a 'rules' list to determine if it applies
    to the current system's OS and architecture.

    Args:
        ruleset: A dictionary that may contain a 'rules' key.
                 Examples include JVM arguments or library definitions.

    Returns:
        True if the rules allow the item for the current system, otherwise False.
    """
    if "rules" not in ruleset:
        # If there are no rules, the default action is to allow.
        return True

    # Default to disallow if rules are present; an 'allow' rule must match.
    allowed = False

    for rule in ruleset["rules"]:
        action = rule.get("action")
        if action == "allow":
            os_conditions = rule.get("os", {})
            
            # If there are no OS conditions, this 'allow' rule is a catch-all.
            if not os_conditions:
                allowed = True
                continue

            # Check if all specified OS conditions match the current system.
            os_name_match = ("name" not in os_conditions or 
                             os_conditions["name"] == _current_os_name)
                             
            os_arch_match = ("arch" not in os_conditions or 
                             os_conditions["arch"] == _current_os_arch)

            if os_name_match and os_arch_match:
                # This 'allow' rule matches the system.
                return True
        
        # Note: A 'disallow' action could be implemented here. If a 'disallow'
        # rule matches, it would immediately return False.
        # elif action == "disallow":
        #     ...

    # If we looped through all rules and only found non-matching 'allow' rules.
    return allowed