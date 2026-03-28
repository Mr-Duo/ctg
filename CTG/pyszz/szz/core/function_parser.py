import logging as log
from typing import Optional
import re
from collections import namedtuple

from config import C_FILE_EXTENSIONS, SOURCE_CODE_OUTPUTS_DIR
from file_manager import get_file_name_with_parent, write_file, join_path, is_path_exist
from helpers import subprocess_cmd

CommentRange = namedtuple('CommentRange', 'start end')
# srcml_file_ext = ['.c', '.h', '.hh', '.hpp', '.hxx', '.cxx', '.cpp', '.cc', '.cs', '.java']

__CACHE_FUNCTIONS = {}


def parse_functions(source_file_path: str):
    if source_file_path not in __CACHE_FUNCTIONS:
        list_functions = parse_functions_srcml(source_file_path)
        __CACHE_FUNCTIONS[source_file_path] = list_functions
    list_functions = __CACHE_FUNCTIONS[source_file_path]
    return list_functions


# def parse_functions_srcml(source_file_path):
#     list_functions = list()

#     if any(source_file_path.endswith(e) for e in C_FILE_EXTENSIONS):
#         source_file_path_srcml_parsed = f"{source_file_path}.xml"
        
#         if is_path_exist(source_file_path_srcml_parsed):
#             with open(source_file_path_srcml_parsed) as f:
#                     stdout = f.read()
#                     stderr = ''
#         else:
#             stdout, stderr = subprocess_cmd(
#                 f'srcml --position {source_file_path}')
        
#         if not stderr:
#             stdout = stdout.replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '')
#             stdout = stdout[stdout.index(">")+1:]
#             outlines =  stdout.splitlines()
#             for i, line in enumerate(outlines):
#                 if len(line) > 0 and len(line[0].strip()) != 0 and line.find("<") > 0:
#                     line = line[line.index("<"):]
#                 if ">class<" in line:
#                     continue
#                 if "<function " in line or "<constructor " in line or "<destructor" in line or\
#                     ((line.startswith("<decl_stmt ") or (("<decl_stmt " in line or "<macro " in line) and "<block" in line)) and
#                         ">;<" not in line and "<argument_list" in line) or \
#                         ((line.startswith("<macro ") or line.startswith("<expr_stmt ")) and ">;<" not in line):
#                     if "</macro> <block" in line:
#                         nLine = line[line.index("</macro> <block"):]
#                         start = int(re.search('pos:start="(\d+):', line).groups()[0])
#                         end = int(re.search('pos:end="(\d+):', nLine).groups()[0])
#                     elif line.startswith("<macro ") and line.endswith("</macro>") and \
#                             i+1 < len(outlines) and outlines[i+1].startswith("<block "):
#                         nLine = outlines[i+1]
#                         start = int(re.search('pos:start="(\d+):', line).groups()[0])
#                         end = int(re.search('pos:end="(\d+):', nLine).groups()[0])
#                     elif line.startswith("<macro ") and "</macro>" not in line:
#                         c = 1
#                         while "</macro>" not in outlines[i+c] or "<block" not in outlines[i+c]:
#                             c += 1
#                             if i + c >= len(outlines)-1:
#                                 break
#                         if c > 5:
#                             start = 0
#                             end = 0
#                         else:
#                             if "<block " in outlines[i+c]:
#                                 nLine = outlines[i+c][outlines[i+c].index("<block "):]
#                             else:
#                                 nLine = line
#                             start = int(re.search('pos:start="(\d+):', line).groups()[0])
#                             end = int(re.search('pos:end="(\d+):', nLine).groups()[0])
#                     else:
#                         start = int(re.search('pos:start="(\d+):', line).groups()[0])
#                         if "<block" in line:
#                             nLine = line[line.index("<block "):]
#                             end = int(re.search('pos:end="(\d+):', nLine).groups()[0])
#                         else:
#                             end = int(re.search('pos:end="(\d+):', line).groups()[0])
#                     if start >= end:
#                         continue
#                     pad = 5
#                     if end - start <= 5:
#                         pad = end - start
#                     function_text = "".join(stdout.splitlines()[start-1:start+pad])
#                     if "</template>" in function_text:
#                         function_text = function_text[function_text.find(
#                             "</template>")+15:]
#                     elif ">template<" in function_text:
#                         function_text = function_text[function_text.find(
#                             ">template<")+20:]
#                     function_text = function_text[:function_text.find("<block")]
                    
#                     token_end = "<argument_list"
#                     if "<function" in line or "<constructor" in line or "<destructor" in line:
#                         token_end = "<parameter_list"
#                     elif line.startswith("<expr_stmt ") and len(outlines[i]) > 0 and\
#                             outlines[i][0] != " " and outlines[i][0] != "<":
#                         token_end = "<expr_stmt"
#                         function_text = ">" + function_text
#                     if token_end not in function_text:
#                         continue
#                     function_text = function_text[:function_text.index(token_end)+20]
#                     token_start = ""
#                     try:
#                         name_xml = re.search(f"{token_start}(.)*{token_end}",function_text)
#                         re_name = re.findall(">([A-z0-9_:]+)<",name_xml.group())
#                         name = ''.join(re_name)
#                     except:
#                         print("="*33)
#                         print(line)
#                         print(source_file_path_srcml_parsed)
#                         continue
#                     if len(list_functions) > 0 and list_functions[-1]["end_line"] > start:
#                         # print("Error parser function: " + list_functions[-1]["name"])
#                         list_functions[-1]["end_line"] = start -1
#                     list_functions.append(
#                         {"name": name, "start_line": start, "end_line": end})
#             write_file(source_file_path_srcml_parsed, stdout, True)
#         else:
#             log.warning(f"Error while parsing file {source_file_path}")
#     else:
#         log.warning(
#             f"File not supported by srcML: {get_file_name_with_parent(source_file_path)}")

#     return list_functions

# Constants
SRCML_PAD_LINES = 5
MACRO_LOOKAHEAD_LIMIT = 5
TEMPLATE_TAG_OFFSET = 15
TOKEN_END_OFFSET = 20


def _extract_line_number(pattern: str, text: str) -> Optional[int]:
    """Safely extract a line number from a srcML position attribute."""
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def _resolve_macro_bounds(outlines: list[str], i: int) -> tuple[int, int]:
    """
    Determine start/end lines for macro declarations that may span
    multiple XML lines before their associated block.
    """
    line = outlines[i]

    # Case 1: macro and block on the same line
    if "</macro> <block" in line:
        block_segment = line[line.index("</macro> <block"):]
        start = _extract_line_number(r'pos:start="(\d+):', line)
        end = _extract_line_number(r'pos:end="(\d+):', block_segment)
        return start, end

    # Case 2: macro closes on this line, block starts on the next
    if line.endswith("</macro>") and i + 1 < len(outlines):
        next_line = outlines[i + 1]
        if next_line.startswith("<block "):
            start = _extract_line_number(r'pos:start="(\d+):', line)
            end = _extract_line_number(r'pos:end="(\d+):', next_line)
            return start, end

    # Case 3: macro spans multiple lines — scan ahead for closing macro + block
    c = 1
    while i + c < len(outlines) - 1:
        candidate = outlines[i + c]
        if "</macro>" in candidate or "<block" in candidate:
            break
        c += 1

    if c > MACRO_LOOKAHEAD_LIMIT:
        return 0, 0

    target_line = outlines[i + c]
    block_segment = (
        target_line[target_line.index("<block "):]
        if "<block " in target_line
        else line
    )
    start = _extract_line_number(r'pos:start="(\d+):', line)
    end = _extract_line_number(r'pos:end="(\d+):', block_segment)
    return start, end


def _resolve_line_bounds(line: str, outlines: list[str], i: int) -> tuple[int, int]:
    """Dispatch to the correct line-bound extraction strategy for a given XML line."""
    if line.startswith("<macro "):
        return _resolve_macro_bounds(outlines, i)

    start = _extract_line_number(r'pos:start="(\d+):', line)
    if "<block" in line:
        block_segment = line[line.index("<block "):]
        end = _extract_line_number(r'pos:end="(\d+):', block_segment)
    else:
        end = _extract_line_number(r'pos:end="(\d+):', line)

    return start, end


def _is_function_line(line: str) -> bool:
    """Return True if this XML line represents a parseable function-like declaration."""
    if ">class<" in line:
        return False
    if "<function " in line or "<constructor " in line or "<destructor" in line:
        return True
    is_decl = (
        line.startswith("<decl_stmt ")
        or (("<decl_stmt " in line or "<macro " in line) and "<block" in line)
    )
    if is_decl and ">;<" not in line and "<argument_list" in line:
        return True
    if (line.startswith("<macro ") or line.startswith("<expr_stmt ")) and ">;<" not in line:
        return True
    return False


def _extract_function_name(
    line: str,
    outlines: list[str],
    i: int,
    start: int,
    stdout_lines: list[str],
) -> Optional[str]:
    """
    Reconstruct a snippet of source around the declaration start and
    extract the function/macro name from it.
    """
    pad = min(SRCML_PAD_LINES, (len(stdout_lines) - start))
    snippet = "".join(stdout_lines[start - 1 : start + pad])

    # Strip leading template declarations
    if "</template>" in snippet:
        snippet = snippet[snippet.find("</template>") + TEMPLATE_TAG_OFFSET:]
    elif ">template<" in snippet:
        snippet = snippet[snippet.find(">template<") + TOKEN_END_OFFSET:]

    snippet = snippet[: snippet.find("<block")]

    # Choose the correct end-token based on declaration type
    if "<function" in line or "<constructor" in line or "<destructor" in line:
        token_end = "<parameter_list"
    elif (
        line.startswith("<expr_stmt ")
        and outlines[i]
        and outlines[i][0] not in (" ", "<")
    ):
        token_end = "<expr_stmt"
        snippet = ">" + snippet
    else:
        token_end = "<argument_list"

    if token_end not in snippet:
        return None

    snippet = snippet[: snippet.index(token_end) + TOKEN_END_OFFSET]

    name_match = re.search(rf"(.)*{token_end}", snippet)
    if not name_match:
        return None

    name_parts = re.findall(r">([A-Za-z0-9_:]+)<", name_match.group())
    return "".join(name_parts) or None


def _get_srcml_output(source_file_path: str) -> tuple[str, str]:
    """Return (stdout, stderr) for srcML, using a cached .xml file if available."""
    cached_path = f"{source_file_path}.xml"
    if is_path_exist(cached_path):
        with open(cached_path) as f:
            return f.read(), ""
    return subprocess_cmd(f"srcml --position {source_file_path}")


def _strip_xml_declaration(stdout: str) -> str:
    """Remove the XML declaration header and root open tag from srcML output."""
    stdout = stdout.replace(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ""
    )
    return stdout[stdout.index(">") + 1:]


def parse_functions_srcml(source_file_path: str) -> list[dict]:
    """
    Parse a C/C++ source file using srcML and return a list of
    function-like declarations with their name and line range.

    Returns:
        List of {"name": str, "start_line": int, "end_line": int}
    """
    if not any(source_file_path.endswith(e) for e in C_FILE_EXTENSIONS):
        log.warning(
            "File not supported by srcML: %s",
            get_file_name_with_parent(source_file_path),
        )
        return []

    stdout, stderr = _get_srcml_output(source_file_path)
    if stderr:
        log.warning("Error while parsing file %s: %s", source_file_path, stderr)
        return []

    stdout = _strip_xml_declaration(stdout)
    cached_path = f"{source_file_path}.xml"

    # Only write cache if it didn't already exist
    if not is_path_exist(cached_path):
        write_file(cached_path, stdout, True)

    outlines = stdout.splitlines()
    list_functions: list[dict] = []

    for i, line in enumerate(outlines):
        # Normalize indented lines to start at their first XML tag
        if line and line[0].strip() and "<" in line and line.find("<") > 0:
            line = line[line.index("<"):]

        if not _is_function_line(line):
            continue

        start, end = _resolve_line_bounds(line, outlines, i)

        if not start or not end or start >= end:
            continue

        name = _extract_function_name(line, outlines, i, start, outlines)
        if not name:
            log.debug("Could not extract name from line %d in %s", i, source_file_path)
            continue

        # Patch the previous entry's end_line if it overlaps
        if list_functions and list_functions[-1]["end_line"] > start:
            list_functions[-1]["end_line"] = start - 1

        list_functions.append({"name": name, "start_line": start, "end_line": end})

    return list_functions


def parse_functions_content(file_name, text):
    if text is None:
        return []
    text = text.replace('\\\n',"\n//")
    text = text.replace('\n#',"\n//")
    text = text.replace("~","")
    text = text.replace("static ","")#explicit 
    text = text.replace("explicit ","")#explicit 
    text = text.replace(" * "," ")
    text = re.sub('\n([ ])+\"(.)+\"\);',"\n//"+"X",text)
    
    regex = '\n(.*){[A-z0-9_:.,\" ]*}(.*)\n'
    res = re.search(regex,text)
    while res is not None:
        text = text.replace(res.group(),"\n" + " ".join(res.groups()) + "\n")
        res = re.search(regex,text)
    
    file_path = join_path(SOURCE_CODE_OUTPUTS_DIR, file_name)
    file_path = write_file(file_path, text, True)
    return parse_functions(file_path)
