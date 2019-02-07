import typing


def drop(line: str, match: typing.Match):
    return ""


def copy(line: str, match: typing.Match):
    return "{}".format(line)


def comment_out_closure(comment_before: str, comment_after: str = None):
    if comment_after is None:
        comment_after = ""
        
    def comment_out(line: str, match: typing.Match):
        return "{} {} {}".format(comment_before, line, comment_after)
    return comment_out


def copy_then_format_closure(format: str):
    format_replace = format_replace_closure(format)
    def copy_then_format(line: str, match: typing.Match):
        return copy(line, match) + format_replace(line, match)
    
    return copy_then_format


def comment_then_format_closure(format: str, comment_before: str, comment_after: str = None):
    format_replace = format_replace_closure(format)
    comment_out = comment_out_closure(comment_before, comment_after)

    def comment_then_format(line: str, match: typing.Match):
        return comment_out(line, match) + format_replace(line, match)
    return comment_then_format


def format_replace_closure(format: str):
    def format_replace(line: str, match: typing.Match):
        return format.format(*match.groups)

    return format_replace

