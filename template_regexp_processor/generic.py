import re
import typing
from template_regexp_processor import transf



class GenericRegExpProcessor:
    enabled_user_rules: dict
    all_user_rules: dict
    command_test: typing.Pattern
    commands: dict
    n_skip: int
    on: bool
    discard: int

    def __init__(self):
        self.comment_begin = None
        self.comment_end = None
        
        self.command_test = None
        self.commands = dict()
        
        self.on = False
        self.discard = False
        self.all_user_rules = dict()
        self.enabled_user_rules = dict()
        self.n_skip = 0

    def enable_rule(self, rule_name: str):
        if rule_name == 'all':
            self.enabled_user_rules = dict(self.all_user_rules)
        else:
            r = self.all_user_rules.get(rule_name)
            if r is None:
                raise ValueError("Can't enable unknown rule '{}'.".format(rule_name))
        
            self.enabled_user_rules[rule_name] = r

    def disable_rule(self, rule_name: str):
        if rule_name == 'all':
            self.enabled_user_rules = dict()
        else:
            if rule_name in self.enabled_user_rules.keys():
                del self.enabled_user_rules[rule_name]

    def on(self):
        self.on = True
    
    def off(self):
        self.on = False

    def inline_command(self, match: typing.Match):
        gs = match.groups()
        command = gs[0]
        arg = gs[1] if len(gs) >= 2 else None
        
        cmd = None
        if arg:
            arg = arg.strip()
            cmd = self.enable_rule if command == 'enable' else cmd
            cmd = self.disable_rule if command == 'disable' else cmd
            if cmd:
                rule_names = arg.split(',')
                for r in rule_names:
                    cmd(r.strip())
            elif command == 'skip':
                self.n_skip = int(arg)
            elif command == 'discard':
                if arg == 'on':
                    self.discard = 1
                elif arg == 'on+':
                    self.discard = 2
                else:
                    self.discard = False
            else:
                raise ValueError("Invalid command with argument '{}'".format(command))
        else:
            cmd = self.on if command == 'on' else cmd
            cmd = self.off if command == 'off' else cmd
            if cmd is None:
                raise ValueError("Invalid command without arguments '{}'".format(command))
        return
    
    def add_rule(self, rule_name: str, rule_func: callable, rule_re: typing.Pattern = None):
        if rule_re is None:
            rule_re = rule_func('get_regexp')
        
        if rule_name == 'all':
            raise ValueError("Rule name 'all' is invalid (reserved).")
        
        self.all_user_rules[rule_name] = self.enabled_user_rules[rule_name] = [rule_re, rule_func]
        return
    
    def inline_add_rule(self, match: typing.Match):
        gs = match.groups()
        if len(gs) != 4:
            raise ValueError("'add_rule' command expects 4 matched groups.")
        rule_name = gs[0]
        rule_re = re.compile(gs[1])
        rule_func = gs[2]
        rule_arg = gs[3]
        
        if not rule_arg:
            rule_arg = None
        
        if rule_func == '=':
            if not rule_arg:
                raise ValueError("Empty fourth group on 'format_replace' transformation.")
            rule_func = transf.format_replace_closure(rule_arg)
        elif rule_func == '+':
            if not gs[3]:
                raise ValueError("Empty fourth group on 'copy_then_format' transformation.")
            rule_func = transf.copy_then_format_closure(rule_arg)
        elif rule_func == '#':
            if rule_arg:
                rule_func = transf.comment_then_format_closure(rule_arg, self.comment_begin, self.comment_end)
            else:
                rule_func = transf.comment_out_closure(self.comment_begin, self.comment_end)
        
        self.add_rule(rule_name, rule_func, rule_re)

    def use_custom_commands(self, command_test: typing.Pattern, commands: dict):
        self.command_test = command_test
        self.commands = commands

    def use_default_commands(self, trailing_exp: str, ending_exp: str,
                             comment_mark_begin: str, comment_mark_end: str = None):
        self.comment_begin = comment_mark_begin
        self.comment_end = "" if comment_mark_end is None else comment_mark_end
        self.command_test = re.compile(trailing_exp + r"\s*regexp-processor\s+(.+?)\s*" + ending_exp)
        self.commands['config'] = [re.compile(r"^(.+?)\s+(.+?)\s*$"), self.inline_command]
        self.commands['switch'] = [re.compile(r"^(.+?)\s*$"), self.inline_command]
        self.commands['add_rule'] = [re.compile(r"^\[(\w+?)\]\s+(.+?)+\s+([+=#])\s*(.*?)\s*$"), self.inline_add_rule]
    
    def run(self, base_file, start_on: bool = True):
        self.on = start_on
        
        for line in base_file:
            if self.n_skip > 0:
                self.n_skip -= 1
                if not self.discard:
                    yield(line)
                continue

            m = self.command_test.match(line)
            if m:
                line = m.group(1)
                for r in self.commands.values():
                    m = r[0].match(line)
                    if m:
                        r[1](m)
                        break
            elif self.on and self.discard != 2:
                for r in self.enabled_user_rules.values():
                    m = r[0].match(line)
                    if m:
                        yield(r[1](line, m))
                        break
            
            if not m and not self.discard:
                yield(line)
