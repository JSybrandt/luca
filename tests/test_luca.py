import pytest
from luca import luca


def test_lex_no_stdout(capfd):
    tokenizer = luca.LucaLexer()
    out, err = capfd.readouterr()
    # This doesn't work.
    assert out == ""
    assert err == ""


def test_lex_newline():
    program = """
    a = 1
    b = 2
    """
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize(program)]
    assert tokens == [
        "NEWLINE",
        "NAME",
        "ASSIGN",
        "NUMBER",
        "NEWLINE",
        "NAME",
        "ASSIGN",
        "NUMBER",
        "NEWLINE",
    ]


def test_lex_ignore_comments():
    program = """# this is a comment.
    true
    # this is a comment."""
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize(program)]
    assert tokens == [
        "NEWLINE",
        "BOOLEAN",
        "NEWLINE",
    ]


def test_lex_tokenize_n_u_l_l():
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize("null nullington")]
    assert tokens == ["NULL", "NAME"]


def test_lex_tokenize_string():
    lexer = luca.LucaLexer()
    tokens = [t.value for t in lexer.tokenize('"this is my test program"')]
    assert tokens == [luca.LucaString("this is my test program")]


def test_lex_tokenize_string_containing_number():
    lexer = luca.LucaLexer()
    tokens = [t.value for t in lexer.tokenize('"12345"')]
    assert tokens == [luca.LucaString("12345")]


def test_lex_tokenize_addition_no_spaces():
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize("1+2")]
    assert tokens == ["NUMBER", "+", "NUMBER"]


def test_lex_tokenize_string_containing_escape_sequence():
    lexer = luca.LucaLexer()
    tokens = [t.value for t in lexer.tokenize(r'"a\t\"b\tc\\"')]
    assert tokens == [luca.LucaString(r"a\t\"b\tc\\")]


def test_lex_tokenize_int():
    lexer = luca.LucaLexer()
    tokens = [t.value for t in lexer.tokenize("12345")]
    assert tokens == [luca.LucaNumber(12345)]


def test_lex_tokenize_float():
    lexer = luca.LucaLexer()
    tokens = [t.value for t in lexer.tokenize("12.345")]
    assert tokens == [luca.LucaNumber(12.345)]


def test_lex_tokenize_float_no_leading_digit():
    lexer = luca.LucaLexer()
    tokens = [t.value for t in lexer.tokenize(".345")]
    assert tokens == [luca.LucaNumber(0.345)]


def test_lex_tokenize_true():
    lexer = luca.LucaLexer()
    tokens = [t.value for t in lexer.tokenize("true")]
    assert tokens == [luca.LucaBool(True)]


def test_lex_tokenize_false():
    lexer = luca.LucaLexer()
    tokens = [t.value for t in lexer.tokenize("false")]
    assert tokens == [luca.LucaBool(False)]


def test_lex_tokenize_return():
    lexer = luca.LucaLexer()
    tokens = [t for t in lexer.tokenize("return")]
    assert len(tokens) == 1
    assert tokens[0].type == "RETURN"


def test_lex_tokenize_assignment_statement():
    program = 'var = "hello darling"'
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize(program)]
    assert tokens == ["NAME", "ASSIGN", "STRING"]


def test_lex_tokenize_add_fn():
    program = "add = (x, y){ return x + y }"
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize(program)]
    assert tokens == [
        "NAME",
        "ASSIGN",
        "(",
        "NAME",
        ",",
        "NAME",
        ")",
        "{",
        "RETURN",
        "NAME",
        "+",
        "NAME",
        "}",
    ]


def test_lex_tokenize_element_access():
    program = 'val["test"] = 35.6'
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize(program)]
    assert tokens == ["NAME", "[", "STRING", "]", "ASSIGN", "NUMBER"]


def test_lex_logic_statement():
    program = "val = foo == not bar and bar != baz or buz"
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize(program)]
    assert tokens == [
        "NAME",
        "ASSIGN",
        "NAME",
        "EQ",
        "NOT",
        "NAME",
        "AND",
        "NAME",
        "NEQ",
        "NAME",
        "OR",
        "NAME",
    ]


def test_lex_print_statement():
    program = 'print "this is a test"'
    lexer = luca.LucaLexer()
    tokens = [t.type for t in lexer.tokenize(program)]
    assert tokens == ["PRINT", "STRING"]


def test_parse_empty_program():
    tokens = luca.LucaLexer().tokenize("")
    luca.LucaParser().parse(tokens)


def test_parse_math_follows_order_of_ops():
    program = "(1+4/2-5*-6)%(12-2)"
    # Should be:
    # (1+4/2-5*-6)%(12-2)
    # = (1+2-5*-6)%10
    # = (1+2-(-30))%10
    # = (3+30)%10 = 3
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaNumber(3)


def test_parse_string_concat():
    program = '"a"+"b"'
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaString("ab")


def test_parse_string_doesnt_work_with_other_bin_ops():
    program = '"a"-"b"'
    tokens = luca.LucaLexer().tokenize(program)
    with pytest.raises(TypeError):
        luca.LucaParser().parse(tokens)


def test_parse_string_subtract_num_error():
    program = '"a"-1'
    tokens = luca.LucaLexer().tokenize(program)
    with pytest.raises(TypeError):
        luca.LucaParser().parse(tokens)


def test_parse_string_times_num_error():
    program = '5*"a"'
    tokens = luca.LucaLexer().tokenize(program)
    with pytest.raises(TypeError):
        luca.LucaParser().parse(tokens)


def test_parse_string_concat_num():
    program = '"a"+5'
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaString("a5")


def test_parse_string_concat_bool():
    program = '"a"+false'
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaString("afalse")


def test_parse_bool_true_and_true():
    program = "true and true"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(True)


def test_parse_bool_true_and_false():
    program = "true and false"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(False)


def test_parse_bool_true_and_error():
    program = "true and 1.0"
    tokens = luca.LucaLexer().tokenize(program)
    with pytest.raises(
        TypeError, match="Cannot perform LucaType.BOOLEAN and LucaType.NUMBER"
    ):
        print(luca.LucaParser().parse(tokens))


def test_parse_bool_false_or_false():
    program = "false or false"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(False)


def test_parse_bool_false_or_true():
    program = "false or true"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(True)


def test_parse_bool_false_or_error():
    program = "false or 1.0"
    tokens = luca.LucaLexer().tokenize(program)
    with pytest.raises(
        TypeError, match="Cannot perform LucaType.BOOLEAN or LucaType.NUMBER"
    ):
        print(luca.LucaParser().parse(tokens))


def test_parse_number_eq():
    program = "1 == 1.0"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(True)

    program = "1 == 2.0"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(False)


def test_parse_string_eq():
    program = '"a" == "a"'
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(True)

    program = '"a" == "b"'
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(False)


def test_parse_bool_eq():
    program = "true == true"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(True)

    program = "true == false"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(False)


def test_parse_null_eq():
    program = "null == null"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(True)


def test_parse_eq_has_lower_precenence_than_math():
    program = "1+2==7-4"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(True)


def test_parse_eq_has_higher_precenence_than_and():
    program = "1==1 and 2==2 and 3==4"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(False)


def test_parse_eq_has_higher_precenence_than_or():
    program = "1==2 or 2==3 or 3==3"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(True)


def test_parse_not():
    program = "not true"
    tokens = luca.LucaLexer().tokenize(program)
    result = luca.LucaParser().parse(tokens)
    assert result == luca.LucaBool(False)


def test_parse_print_bool(capfd):
    program = "print(not true)"
    tokens = luca.LucaLexer().tokenize(program)
    luca.LucaParser().parse(tokens)
    out, _ = capfd.readouterr()
    assert out == "false\n"


def test_parse_print_number(capfd):
    program = "print(2-1)"
    tokens = luca.LucaLexer().tokenize(program)
    luca.LucaParser().parse(tokens)
    out, _ = capfd.readouterr()
    assert out == "1\n"


def test_parse_print_string(capfd):
    program = 'print("hello"+"world")'
    tokens = luca.LucaLexer().tokenize(program)
    luca.LucaParser().parse(tokens)
    out, _ = capfd.readouterr()
    assert out == "helloworld\n"


def test_parse_assignment():
    program = "a = 1"
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(1)
    assert parser.get("a") == luca.LucaNumber(1)


def test_parse_multiple_assignment():
    program = "a = b = 2"
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(2)
    assert parser.get("a") == luca.LucaNumber(2)
    assert parser.get("b") == luca.LucaNumber(2)


def test_parse_with_extra_newlines():
    program = """

      13

    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(13)


def test_parse_blocks_return_last_expression():
    program = """
        1
        2
        3
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(3)


def test_parse_assign_with_extra_whitespace():
    program = """

        a    =    1

    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(1)
    assert parser.get("a") == luca.LucaNumber(1)


def test_parse_multiple_assignments():
    program = """
        a = 1
        b = 2
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(2)
    assert parser.get("a") == luca.LucaNumber(1)
    assert parser.get("b") == luca.LucaNumber(2)


def test_parse_use_variable():
    program = """
        a = 1
        a
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(1)
    assert parser.get("a") == luca.LucaNumber(1)


def test_parse_use_variable_in_math():
    program = """
        a = 1
        a + 1
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(2)
    assert parser.get("a") == luca.LucaNumber(1)


def test_parse_use_variable_in_assignment():
    program = """
        a = 1
        b = a + 1
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(2)
    assert parser.get("a") == luca.LucaNumber(1)
    assert parser.get("b") == luca.LucaNumber(2)


def test_parse_use_variable_in_assignment():
    program = """
        a = 1
        b = a + 1
        c = a + b
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(3)
    assert parser.get("a") == luca.LucaNumber(1)
    assert parser.get("b") == luca.LucaNumber(2)
    assert parser.get("c") == luca.LucaNumber(3)


def test_parse_scope_shadow_variable(capfd):
    program = """
        a = 1
        {
            a = 2
            print(a)
        }
        print(a)
    """
    tokens = luca.LucaLexer().tokenize(program)
    luca.LucaParser().parse(tokens)
    out, _ = capfd.readouterr()
    assert out == "2\n1\n"


def test_parse_reference_outer_scope(capfd):
    program = """
        a = 1
        {
            print(a)
        }
    """
    tokens = luca.LucaLexer().tokenize(program)
    luca.LucaParser().parse(tokens)
    out, _ = capfd.readouterr()
    assert out == "1\n"


def test_parse_scopes_are_objects(capfd):
    program = """
        a = {
            b = 1
            c = 2
        }
        print(a)
    """
    tokens = luca.LucaLexer().tokenize(program)
    luca.LucaParser().parse(tokens)
    out, _ = capfd.readouterr()
    assert out == "{b:1,c:2}(LucaType.OBJECT)\n"


def test_parse_get_value_from_object(capfd):
    program = """
        a = {
            b = 1
            c = 2
        }
        a.c
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(2)


def test_parse_get_multiple_layers_of_indirection(capfd):
    program = """
        a = {
            b = {
                c = {
                  d = 1
                }
            }
        }
        a.b.c.d
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(1)


def test_parse_empty_object(capfd):
    program = """
        a = {}
        print(a)
    """
    tokens = luca.LucaLexer().tokenize(program)
    luca.LucaParser().parse(tokens)
    out, _ = capfd.readouterr()
    assert out == "{}(LucaType.OBJECT)\n"


def test_parse_empty_object(capfd):
    program = """
        a = 1
        b = {}
        b.a  # b is a closure that contains the parent scope.
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(1)


def test_parse_weird_scope_rules():
    program = """
        a = {
            b = 1
        }
        c = {
            d = 1
        }
        a.c.a.c.a.c.d == a.a.a.a.a.a.a.a.a.b
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaBool(True)


def test_parse_add_values_inside_objects():
    program = """
        a = {b = 1}
        c = {d = 2}
        a.b + c.d
    """
    tokens = luca.LucaLexer().tokenize(program)
    parser = luca.LucaParser()
    assert parser.parse(tokens) == luca.LucaNumber(3)
