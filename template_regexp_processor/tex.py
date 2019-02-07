from template_regexp_processor import GenericRegExpProcessor
import re
import typing


class TexJinja2Preprocessor(GenericRegExpProcessor):
    def __init__(self, variable_start_string: str = "((=", variable_end_string: str = "))"):
        super().__init__()
        self.use_default_commands('% ', '$', '%', '')
        self.variable_start_string: str = variable_start_string
        self.variable_end_string: str = variable_end_string
        self.add_rule("def_var", self.def_var())
        
    def def_var(self):
        rexp = re.compile(r"^\\def\\(.+?)\{(.+?)\}\s+\%=\s*(.+?)\s*$")
        fmt = r"\def\{}{{\Q{{ {}{}{} }} }}" + '\n'
        fmt = r"\def\{}{{ {}{}{} }}" + '\n'

        def _def_var(line: str, match: typing.Match = None):
            if line == 'get_regexp' and match is None:
                return rexp
    
            varname: str = match.group(1).strip()
            pyvar: str = match.group(3).strip()
            if pyvar[-1:] == '.':
                pyvar = varname if pyvar == '.' else pyvar + varname
    
            return fmt.format(varname, self.variable_start_string, pyvar, self.variable_end_string)
        
        return _def_var
