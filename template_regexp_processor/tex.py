from template_regexp_processor.generic import GenericRegExpProcessor
import re
import typing



class TexJinja2Preprocessor(GenericRegExpProcessor):
    def __init__(self, jobname: str = None, preproc_ext: str = DEFAULT_PREPROC_EXT):
        super().__init__()
        self.use_default_commands('% ', '', '%', '')
        self.add_rule("def_var", self.def_var)
    
    @classmethod
    def def_var(cls, line: str, match: typing.Match = None):
        if line == 'get_regexp' and match is None:
            return re.compile(r"^\\def\\(.+?)\{(.+?)\}\s+\%=\s*(.+?)\s*$")
        
        varname: str = match.group(1).strip()
        pyvar: str = match.group(3).strip()
        if pyvar[-1:] == '.':
            pyvar = varname if pyvar == '.' else pyvar + varname
        
        return r"\\def\\{}\{{}\}".format(varname, pyvar)
