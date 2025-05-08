import unittest
from tokens import (
    Unit,
    UnitOfLength,
    UnitOfAngle,
    is_delimiter,
    is_safe_delimiter,
    CodePointBuffer,
    BackQuoteString,
    BooleanT,
    DecimalPoint,
    Digit,
    Digit1To9,
    DoubleQuoteString,
    Frac,
    Int,
    Minus,
    NegativeInt,
    NumberT,
    PositiveInt,
    SingleQuoteString,
    StringT,
    Zero,
    OpenBracket,
    CloseBracket,
    NumberUOL,
    NumberUOA,
    Operator,
    Expression,
    Computation,
)


def cpb(s: str) -> CodePointBuffer:
    return CodePointBuffer(s)


class TokensTest(unittest.TestCase):
    def test_token_delimiter_methods(self):
        self.assertTrue(is_delimiter(" "))
        self.assertTrue(is_delimiter(None))
        self.assertFalse(is_delimiter("'"))
        self.assertTrue(is_safe_delimiter(None))
        self.assertTrue(is_safe_delimiter(" "))
        self.assertTrue(is_safe_delimiter(":"))
        self.assertTrue(is_safe_delimiter(","))
        self.assertFalse(is_safe_delimiter("'"))

    def test_backquote_string_valid(self):
        self.assertEqual(BackQuoteString("`\\\\`", "\\"), BackQuoteString.parse(cpb("`\\\\`")))
        self.assertEqual(BackQuoteString("`\\``", "`"), BackQuoteString.parse(cpb("`\\``")))
        self.assertEqual(BackQuoteString("`\\\\\\``", "\\`"), BackQuoteString.parse(cpb("`\\\\\\``")))
        self.assertEqual(
            BackQuoteString("`\\\\\\\\`", "\\\\"),
            BackQuoteString.parse(cpb("`\\\\\\\\`")),
        )
        self.assertEqual(
            BackQuoteString("`test\\\\`", "test\\"),
            BackQuoteString.parse(cpb("`test\\\\`")),
        )
        self.assertEqual(
            BackQuoteString("`test\\``", "test`"),
            BackQuoteString.parse(cpb("`test\\``")),
        )
        self.assertEqual(
            BackQuoteString("`test\\\\\\``", "test\\`"),
            BackQuoteString.parse(cpb("`test\\\\\\``")),
        )
        self.assertEqual(BackQuoteString("``", ""), BackQuoteString.parse(cpb("``")))

    def test_backquote_string_invalid(self):
        self.assertIsNone(BackQuoteString.parse(cpb("test")))
        self.assertIsNone(BackQuoteString.parse(cpb("")))
        self.assertIsNone(BackQuoteString.parse(cpb("234")))
        self.assertIsNone(BackQuoteString.parse(cpb("`")))
        self.assertIsNone(BackQuoteString.parse(cpb("`test")))
        self.assertIsNone(BackQuoteString.parse(cpb("`234")))

    def test_boolean_t_valid(self):
        t = BooleanT.parse(cpb("True"))
        self.assertIsNotNone(t)
        self.assertEqual("True", t.value)  # type: ignore
        self.assertTrue(t.bool)  # type: ignore

        self.assertEqual(BooleanT("True", True), BooleanT.parse(cpb("True")))
        self.assertEqual(BooleanT("true", True), BooleanT.parse(cpb("true")))
        self.assertEqual(BooleanT("False", False), BooleanT.parse(cpb("False")))
        self.assertEqual(BooleanT("false", False), BooleanT.parse(cpb("false")))
        self.assertEqual(BooleanT("True", True), BooleanT.parse(cpb("True ")))
        self.assertEqual(BooleanT("TrUe", True), BooleanT.parse(cpb("TrUe ")))
        self.assertEqual(BooleanT("fAlse", False), BooleanT.parse(cpb("fAlse")))

    def test_boolean_t_invalid(self):
        self.assertIsNone(BooleanT.parse(cpb("")))
        self.assertIsNone(BooleanT.parse(cpb("1")))
        self.assertIsNone(BooleanT.parse(cpb("0")))
        self.assertIsNone(BooleanT.parse(cpb(" ")))
        self.assertIsNone(BooleanT.parse(cpb(" True")))
        self.assertIsNone(BooleanT.parse(cpb("")))

    def test_decimal_point_valid(self):
        self.assertEqual(DecimalPoint(), DecimalPoint.parse(cpb(".")))
        self.assertEqual(DecimalPoint(), DecimalPoint.parse(cpb(". ")))
        self.assertEqual(DecimalPoint(), DecimalPoint.parse(cpb(".a")))
        self.assertEqual(DecimalPoint(), DecimalPoint.parse(cpb(".123")))

    def test_decimal_point_invalid(self):
        self.assertIsNone(DecimalPoint.parse(cpb(" .")))
        self.assertIsNone(DecimalPoint.parse(cpb("0")))
        self.assertIsNone(DecimalPoint.parse(cpb(" ")))
        self.assertIsNone(DecimalPoint.parse(cpb("a")))
        self.assertIsNone(DecimalPoint.parse(cpb("")))
        self.assertIsNone(DecimalPoint.parse(cpb("1 ")))
        self.assertIsNone(DecimalPoint.parse(cpb("-1")))
        self.assertIsNone(DecimalPoint.parse(cpb("1")))

    def test_digit1_to9_valid(self):
        self.assertEqual(Digit1To9("1"), Digit1To9.parse(cpb("1")))
        self.assertEqual(Digit1To9("2"), Digit1To9.parse(cpb("2")))
        self.assertEqual(Digit1To9("3"), Digit1To9.parse(cpb("3")))
        self.assertEqual(Digit1To9("4"), Digit1To9.parse(cpb("4")))
        self.assertEqual(Digit1To9("5"), Digit1To9.parse(cpb("5")))
        self.assertEqual(Digit1To9("6"), Digit1To9.parse(cpb("6")))
        self.assertEqual(Digit1To9("7"), Digit1To9.parse(cpb("7")))
        self.assertEqual(Digit1To9("8"), Digit1To9.parse(cpb("8")))
        self.assertEqual(Digit1To9("9"), Digit1To9.parse(cpb("9")))
        self.assertEqual(Digit1To9("1"), Digit1To9.parse(cpb("10")))
        self.assertEqual(Digit1To9("1"), Digit1To9.parse(cpb("1 ")))

    def test_digit1_to9_invalid(self):
        self.assertIsNone(Digit1To9.parse(cpb("0")))
        self.assertIsNone(Digit1To9.parse(cpb(" 1")))
        self.assertIsNone(Digit1To9.parse(cpb("a")))
        self.assertIsNone(Digit1To9.parse(cpb("A")))
        self.assertIsNone(Digit1To9.parse(cpb("")))
        self.assertIsNone(Digit1To9.parse(cpb("-1")))
        self.assertIsNone(Digit1To9.parse(cpb(".123")))

    def test_digit_valid(self):
        self.assertEqual(Digit("0"), Digit.parse(cpb("0")))
        self.assertEqual(Digit("1"), Digit.parse(cpb("1")))
        self.assertEqual(Digit("2"), Digit.parse(cpb("2")))
        self.assertEqual(Digit("3"), Digit.parse(cpb("3")))
        self.assertEqual(Digit("4"), Digit.parse(cpb("4")))
        self.assertEqual(Digit("5"), Digit.parse(cpb("5")))
        self.assertEqual(Digit("6"), Digit.parse(cpb("6")))
        self.assertEqual(Digit("7"), Digit.parse(cpb("7")))
        self.assertEqual(Digit("8"), Digit.parse(cpb("8")))
        self.assertEqual(Digit("9"), Digit.parse(cpb("9")))
        self.assertEqual(Digit("1"), Digit.parse(cpb("1 ")))

    def test_digit_invalid(self):
        self.assertIsNone(Digit.parse(cpb("")))
        self.assertIsNone(Digit.parse(cpb("-1")))
        self.assertIsNone(Digit.parse(cpb("a")))
        self.assertIsNone(Digit.parse(cpb("A")))
        self.assertIsNone(Digit.parse(cpb(" ")))
        self.assertIsNone(Digit.parse(cpb(" 1")))
        self.assertIsNone(Digit.parse(cpb(".22")))

    def test_double_quote_string_valid(self):
        t = DoubleQuoteString('"test"', "test")
        self.assertEqual('"test"', t.value)
        self.assertEqual("test", t.content)

        self.assertEqual(DoubleQuoteString('"\\\\"', "\\"), DoubleQuoteString.parse(cpb('"\\\\"')))
        self.assertEqual(DoubleQuoteString('"\\""', '"'), DoubleQuoteString.parse(cpb('"\\""')))
        self.assertEqual(
            DoubleQuoteString('"\\\\\\""', '\\"'),
            DoubleQuoteString.parse(cpb('"\\\\\\""')),
        )
        self.assertEqual(
            DoubleQuoteString('"\\\\\\\\"', "\\\\"),
            DoubleQuoteString.parse(cpb('"\\\\\\\\"')),
        )
        self.assertEqual(
            DoubleQuoteString('"test\\\\"', "test\\"),
            DoubleQuoteString.parse(cpb('"test\\\\"')),
        )
        self.assertEqual(
            DoubleQuoteString('"test\\""', 'test"'),
            DoubleQuoteString.parse(cpb('"test\\""')),
        )
        self.assertEqual(
            DoubleQuoteString('"test\\\\\\""', 'test\\"'),
            DoubleQuoteString.parse(cpb('"test\\\\\\""')),
        )
        self.assertEqual(DoubleQuoteString('""', ""), DoubleQuoteString.parse(cpb('""')))

    def test_double_quote_string_invalid(self):
        self.assertIsNone(DoubleQuoteString.parse(cpb("test")))
        self.assertIsNone(DoubleQuoteString.parse(cpb("")))
        self.assertIsNone(DoubleQuoteString.parse(cpb("234")))
        self.assertIsNone(DoubleQuoteString.parse(cpb('"')))
        self.assertIsNone(DoubleQuoteString.parse(cpb('"test')))
        self.assertIsNone(DoubleQuoteString.parse(cpb('"234')))

    def test_frac_valid(self):
        self.assertEqual(Frac(".14"), Frac.parse(cpb(".14")))
        self.assertEqual(Frac(".14"), Frac.parse(cpb(".14.15")))
        self.assertEqual(Frac(".14"), Frac.parse(cpb(".14 ")))
        self.assertEqual(Frac(".14"), Frac.parse(cpb(".14abc")))
        self.assertEqual(Frac(".14"), Frac.parse(cpb(".14\\")))
        self.assertEqual(Frac(".14"), Frac.parse(cpb(".14'")))

    def test_frac_invalid(self):
        self.assertIsNone(Frac.parse(cpb(".")))
        self.assertIsNone(Frac.parse(cpb("14")))
        self.assertIsNone(Frac.parse(cpb("")))
        self.assertIsNone(Frac.parse(cpb(" ")))
        self.assertIsNone(Frac.parse(cpb("abc")))
        self.assertIsNone(Frac.parse(cpb("-123")))
        self.assertIsNone(Frac.parse(cpb("3.14")))

    def test_int_valid(self):
        self.assertEqual(Int("0"), Int.parse(cpb("0")))
        self.assertEqual(Int("123"), Int.parse(cpb("123")))
        self.assertEqual(Int("0"), Int.parse(cpb("0 ")))
        self.assertEqual(Int("123"), Int.parse(cpb("123 ")))
        self.assertEqual(Int("0"), Int.parse(cpb("0.16")))
        self.assertEqual(Int("3"), Int.parse(cpb("3.14")))

    def test_int_invalid(self):
        self.assertIsNone(Int.parse(cpb("abc")))
        self.assertIsNone(Int.parse(cpb("")))
        self.assertIsNone(Int.parse(cpb(" ")))
        self.assertIsNone(Int.parse(cpb(".14")))

    def test_minus_valid(self):
        self.assertEqual(Minus(), Minus.parse(cpb("-")))
        self.assertEqual(Minus(), Minus.parse(cpb("- ")))

    def test_minus_invalid(self):
        self.assertIsNone(Minus.parse(cpb("")))
        self.assertIsNone(Minus.parse(cpb("0")))
        self.assertIsNone(Minus.parse(cpb(" -")))
        self.assertIsNone(Minus.parse(cpb("a")))
        self.assertIsNone(Minus.parse(cpb("1")))
        self.assertIsNone(Minus.parse(cpb("a-")))
        self.assertIsNone(Minus.parse(cpb("1-")))

    def test_negative_int_valid(self):
        self.assertEqual(NegativeInt("-123"), NegativeInt.parse(cpb("-123")))
        self.assertEqual(NegativeInt("-123"), NegativeInt.parse(cpb("-123abc")))
        self.assertEqual(NegativeInt("-123"), NegativeInt.parse(cpb("-123 ")))
        self.assertEqual(NegativeInt("-123"), NegativeInt.parse(cpb("-123 456")))
        self.assertEqual(NegativeInt("-3"), NegativeInt.parse(cpb("-3.14")))

    def test_negative_int_invalid(self):
        self.assertIsNone(NegativeInt.parse(cpb("abc")))
        self.assertIsNone(NegativeInt.parse(cpb("")))
        self.assertIsNone(NegativeInt.parse(cpb("123")))
        self.assertIsNone(NegativeInt.parse(cpb("0123")))
        self.assertIsNone(NegativeInt.parse(cpb(".14")))

    def test_number_t_valid(self):
        number = NumberT.parse(cpb("0"))
        self.assertIsNotNone(number)
        self.assertEqual("0", number.value)  # type: ignore
        self.assertTrue(number.is_positive)  # type: ignore
        self.assertFalse(number.is_double)  # type: ignore

        self.assertEqual(14, NumberT.parse(cpb("14a")).to_int())  # type: ignore
        self.assertEqual(NumberT("0", True, False), NumberT.parse(cpb("0")))
        self.assertEqual(NumberT("-0.123", False, True), NumberT.parse(cpb("-0.123")))
        self.assertEqual(NumberT("-14", False, False), NumberT.parse(cpb("-14")))
        self.assertEqual(NumberT("14", True, False), NumberT.parse(cpb("14")))
        self.assertEqual(NumberT("3.14", True, True), NumberT.parse(cpb("3.14 ")))
        self.assertEqual(NumberT("-3.14", False, True), NumberT.parse(cpb("-3.14")))
        self.assertEqual(NumberT("14", True, False), NumberT.parse(cpb("14\\")))
        self.assertEqual(NumberT("14", True, False), NumberT.parse(cpb("14'")))
        self.assertEqual(NumberT("14", True, False), NumberT.parse(cpb('14"')))
        self.assertEqual(NumberT("14", True, False), NumberT.parse(cpb("14 ")))
        self.assertEqual(NumberT("-14", False, False), NumberT.parse(cpb("-14\\")))
        self.assertEqual(NumberT("-14", False, False), NumberT.parse(cpb("-14'")))
        self.assertEqual(NumberT("-14", False, False), NumberT.parse(cpb('-14"')))
        self.assertEqual(NumberT("-14", False, False), NumberT.parse(cpb("-14 ")))
        self.assertEqual(NumberT("3.14", True, True), NumberT.parse(cpb("3.14\\")))
        self.assertEqual(NumberT("3.14", True, True), NumberT.parse(cpb("3.14'")))
        self.assertEqual(NumberT("3.14", True, True), NumberT.parse(cpb('3.14"')))
        self.assertEqual(NumberT("3.14", True, True), NumberT.parse(cpb("3.14 ")))
        self.assertEqual(NumberT("-3.14", False, True), NumberT.parse(cpb("-3.14\\")))
        self.assertEqual(NumberT("-3.14", False, True), NumberT.parse(cpb("-3.14'")))
        self.assertEqual(NumberT("-3.14", False, True), NumberT.parse(cpb('-3.14"')))
        self.assertEqual(NumberT("-3.14", False, True), NumberT.parse(cpb("-3.14 ")))

    def test_number_t_invalid(self):
        self.assertIsNone(NumberT.parse(cpb("-")))
        self.assertIsNone(NumberT.parse(cpb("")))
        self.assertIsNone(NumberT.parse(cpb(" ")))
        self.assertIsNone(NumberT.parse(cpb("a")))
        self.assertIsNone(NumberT.parse(cpb("a14")))
        self.assertIsNone(NumberT.parse(cpb("a3.14")))
        self.assertIsNone(NumberT.parse(cpb("a-14")))
        self.assertIsNone(NumberT.parse(cpb("a-3.14")))
        self.assertIsNone(NumberT.parse(cpb("a14 ")))
        self.assertIsNone(NumberT.parse(cpb("a3.14 ")))
        self.assertIsNone(NumberT.parse(cpb("a-14 ")))
        self.assertIsNone(NumberT.parse(cpb("a-3.14 ")))

    def test_positive_int_valid(self):
        self.assertEqual(PositiveInt("123"), PositiveInt.parse(cpb("123")))
        self.assertEqual(PositiveInt("123"), PositiveInt.parse(cpb("123abc")))
        self.assertEqual(PositiveInt("123"), PositiveInt.parse(cpb("123 ")))
        self.assertEqual(PositiveInt("123"), PositiveInt.parse(cpb("123 456")))
        self.assertEqual(PositiveInt("3"), PositiveInt.parse(cpb("3.14")))

    def test_positive_int_invalid(self):
        self.assertIsNone(PositiveInt.parse(cpb("abc")))
        self.assertIsNone(PositiveInt.parse(cpb("")))
        self.assertIsNone(PositiveInt.parse(cpb("-1")))
        self.assertIsNone(PositiveInt.parse(cpb("0123")))
        self.assertIsNone(PositiveInt.parse(cpb(".14")))

    def test_single_quote_string_valid(self):
        self.assertEqual(SingleQuoteString("'\\\\'", "\\"), SingleQuoteString.parse(cpb("'\\\\'")))
        self.assertEqual(SingleQuoteString("'\\''", "'"), SingleQuoteString.parse(cpb("'\\'')")))
        self.assertEqual(
            SingleQuoteString("'\\\\\\''", "\\'"),
            SingleQuoteString.parse(cpb("'\\\\\\'')")),
        )
        self.assertEqual(
            SingleQuoteString("'\\\\\\\\'", "\\\\"),
            SingleQuoteString.parse(cpb("'\\\\\\\\'")),
        )
        self.assertEqual(
            SingleQuoteString("'test\\\\'", "test\\"),
            SingleQuoteString.parse(cpb("'test\\\\'")),
        )
        self.assertEqual(
            SingleQuoteString("'test\\''", "test'"),
            SingleQuoteString.parse(cpb("'test\\'')")),
        )
        self.assertEqual(
            SingleQuoteString("'test\\\\\\''", "test\\'"),
            SingleQuoteString.parse(cpb("'test\\\\\\'')")),
        )
        self.assertEqual(SingleQuoteString("''", ""), SingleQuoteString.parse(cpb("''")))

    def test_single_quote_string_invalid(self):
        self.assertIsNone(SingleQuoteString.parse(cpb("test")))
        self.assertIsNone(SingleQuoteString.parse(cpb("")))
        self.assertIsNone(SingleQuoteString.parse(cpb("234")))
        self.assertIsNone(SingleQuoteString.parse(cpb("'")))
        self.assertIsNone(SingleQuoteString.parse(cpb("'test")))
        self.assertIsNone(SingleQuoteString.parse(cpb("'234")))

    def test_string_t_valid(self):
        self.assertEqual(StringT("test"), StringT.parse(cpb("test")))
        self.assertEqual(StringT(""), StringT.parse(cpb(" ")))
        self.assertEqual(StringT("test"), StringT.parse(cpb("test test")))
        self.assertEqual(StringT("test"), StringT.parse(cpb("'test'")))
        self.assertEqual(StringT("test"), StringT.parse(cpb('"test"')))
        self.assertEqual(StringT("\\"), StringT.parse(cpb("'\\\\'")))
        self.assertEqual(StringT("'"), StringT.parse(cpb("'\\'')")))
        self.assertEqual(StringT("\\"), StringT.parse(cpb('"\\\\"')))
        self.assertEqual(StringT('"'), StringT.parse(cpb("'\\\"')")))
        self.assertEqual(StringT("\\test"), StringT.parse(cpb("'\\\\test'")))
        self.assertEqual(StringT("\\test"), StringT.parse(cpb('"\\\\test"')))

    def test_string_t_invalid(self):
        self.assertIsNone(StringT.parse(cpb("")))
        self.assertIsNone(StringT.parse(cpb("'")))
        self.assertIsNone(StringT.parse(cpb('"')))
        self.assertIsNone(StringT.parse(cpb("'test")))
        self.assertIsNone(StringT.parse(cpb('"test')))
        self.assertIsNone(StringT.parse(cpb("'test\"")))
        self.assertIsNone(StringT.parse(cpb("\"test'")))

    def test_zero_valid(self):
        self.assertEqual(Zero("0"), Zero.parse(cpb("0")))
        self.assertEqual(Zero("0"), Zero.parse(cpb("0 ")))

    def test_zero_invalid(self):
        self.assertIsNone(Zero.parse(cpb("1")))
        self.assertIsNone(Zero.parse(cpb("a")))
        self.assertIsNone(Zero.parse(cpb(" ")))
        self.assertIsNone(Zero.parse(cpb("")))
        self.assertIsNone(Zero.parse(cpb("-")))
        self.assertIsNone(Zero.parse(cpb(" 0")))

    def test_number_with_unit_valid(self):
        # Helper functions for creating instances
        def n(n_str, u=None):
            return NumberUOL(n_str, u)

        def nmm(n_str):
            return NumberUOL(n_str, UnitOfLength.Millimeter)

        self.assertEqual(n("0", None), NumberUOL.parse(cpb("0")))
        self.assertEqual(n("-0.123", None), NumberUOL.parse(cpb("-0.123")))
        self.assertEqual(n("100", None), NumberUOL.parse(cpb("100")))
        self.assertEqual(n("3.14", None), NumberUOL.parse(cpb("3.14")))
        self.assertEqual(n("31.4", None), NumberUOL.parse(cpb("31.4")))
        self.assertEqual(n("-31.4", None), NumberUOL.parse(cpb("-31.4")))
        self.assertEqual(n("0", UnitOfLength.Millimeter), NumberUOL.parse(cpb("0mm")))
        self.assertEqual(n("-0.123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("-0.123mm")))
        self.assertEqual(n("123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("123mm+")))
        self.assertEqual(n("123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("123mm(")))
        self.assertEqual(n("123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("123mm +")))
        self.assertEqual(n("123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("123 mm +")))
        self.assertEqual(n("123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("123 mm+")))
        self.assertEqual(n("-123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("-123mm")))
        self.assertEqual(n("-123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("-123 mm")))
        self.assertEqual(n("-123", UnitOfLength.Millimeter), NumberUOL.parse(cpb("-123 mm ")))
        self.assertEqual(n("-123.45", UnitOfLength.Millimeter), NumberUOL.parse(cpb("-123.45  mm")))
        self.assertEqual(n("123.45", UnitOfLength.Centimeter), NumberUOL.parse(cpb("123.45cm")))
        self.assertEqual(n("123.45", UnitOfLength.Meter), NumberUOL.parse(cpb("123.45m")))
        self.assertEqual(n("123.45", UnitOfLength.Inch), NumberUOL.parse(cpb("123.45in")))
        self.assertEqual(n("123.45", UnitOfLength.Inch), NumberUOL.parse(cpb("123.45inch")))
        self.assertEqual(n("123.45", UnitOfLength.Foot), NumberUOL.parse(cpb("123.45ft")))
        self.assertEqual(n("123.45", UnitOfLength.Foot), NumberUOL.parse(cpb("123.45foot")))
        self.assertEqual(n("123.45", UnitOfLength.Foot), NumberUOL.parse(cpb("123.45feet")))
        self.assertEqual(n("123.45", UnitOfLength.Foot), NumberUOL.parse(cpb("123.45   feet")))

    def test_number_with_uoa_valid(self):
        # Helper function for creating UOA instances
        def n(n_str, u=None):
            return NumberUOA(n_str, u)

        self.assertEqual(n("0", None), NumberUOA.parse(cpb("0")))
        self.assertEqual(n("-0.123", None), NumberUOA.parse(cpb("-0.123")))
        self.assertEqual(n("100", None), NumberUOA.parse(cpb("100")))
        self.assertEqual(n("3.14", None), NumberUOA.parse(cpb("3.14")))
        self.assertEqual(n("31.4", None), NumberUOA.parse(cpb("31.4")))
        self.assertEqual(n("-31.4", None), NumberUOA.parse(cpb("-31.4")))
        self.assertEqual(n("0", UnitOfAngle.Degree), NumberUOA.parse(cpb("0deg")))
        self.assertEqual(n("123", UnitOfAngle.Degree), NumberUOA.parse(cpb("123deg")))
        self.assertEqual(n("123", UnitOfAngle.Degree), NumberUOA.parse(cpb("123deg(")))
        self.assertEqual(n("123", UnitOfAngle.Degree), NumberUOA.parse(cpb("123deg +")))
        self.assertEqual(n("123", UnitOfAngle.Degree), NumberUOA.parse(cpb("123 deg +")))
        self.assertEqual(n("123", UnitOfAngle.Degree), NumberUOA.parse(cpb("123 deg+")))
        self.assertEqual(n("-123", UnitOfAngle.Degree), NumberUOA.parse(cpb("-123deg")))
        self.assertEqual(n("-123", UnitOfAngle.Degree), NumberUOA.parse(cpb("-123 deg")))
        self.assertEqual(n("-123", UnitOfAngle.Degree), NumberUOA.parse(cpb("-123 deg ")))
        self.assertEqual(n("-123.45", UnitOfAngle.Radian), NumberUOA.parse(cpb("-123.45  rad")))
        self.assertEqual(n("123.45", UnitOfAngle.Radian), NumberUOA.parse(cpb("123.45rad")))

    def test_number_with_unit_invalid(self):
        self.assertIsNone(NumberUOL.parse(cpb("0mmm")))
        self.assertIsNone(NumberUOL.parse(cpb("0 mmm")))
        self.assertIsNone(NumberUOL.parse(cpb("0 456")))
        self.assertIsNone(NumberUOA.parse(cpb("0mm")))
        self.assertIsNone(NumberUOL.parse(cpb("0reg")))

    def test_open_bracket_valid(self):
        self.assertEqual(OpenBracket(), OpenBracket.parse(cpb("(")))
        self.assertEqual(OpenBracket(), OpenBracket.parse(cpb("( ")))
        self.assertEqual(OpenBracket(), OpenBracket.parse(cpb("((")))

    def test_open_bracket_invalid(self):
        self.assertIsNone(OpenBracket.parse(cpb(")")))
        self.assertIsNone(OpenBracket.parse(cpb(") ")))

    def test_close_bracket_valid(self):
        self.assertNotEqual(OpenBracket(), CloseBracket.parse(cpb(")")))
        self.assertEqual(CloseBracket(), CloseBracket.parse(cpb(")")))
        self.assertEqual(CloseBracket(), CloseBracket.parse(cpb(") ")))

    def test_close_bracket_invalid(self):
        self.assertIsNone(CloseBracket.parse(cpb("(")))
        self.assertIsNone(CloseBracket.parse(cpb("( ")))

    def test_operator_valid(self):
        self.assertEqual(Operator("+"), Operator.parse(cpb("+")))
        self.assertEqual(Operator("-"), Operator.parse(cpb("-")))
        self.assertEqual(Operator("*"), Operator.parse(cpb("*")))
        self.assertEqual(Operator("/"), Operator.parse(cpb("/")))
        self.assertEqual(Operator("+"), Operator.parse(cpb("+1")))
        self.assertEqual(Operator("-"), Operator.parse(cpb("-1")))
        self.assertEqual(Operator("-"), Operator.parse(cpb("- 1")))

    def test_operator_invalid(self):
        self.assertIsNone(Operator.parse(cpb("1+")))
        self.assertIsNone(Operator.parse(cpb("(")))

    def test_expression_valid(self):
        # Helper functions for creating instances
        def n(n_str, u=None):
            return NumberUOL(n_str, u)

        def nmm(n_str):
            return NumberUOL(n_str, UnitOfLength.Millimeter)

        def o(o_str):
            return Operator(o_str)

        ob = OpenBracket()
        cb = CloseBracket()

        self.assertEqual(Expression([n("123")]), Expression.parse_with(cpb("123"), NumberUOL.parse))
        self.assertEqual(Expression([n("123")]), Expression.parse_with(cpb("123)"), NumberUOL.parse))
        self.assertEqual(Expression([n("123")]), Expression.parse_with(cpb("123 )"), NumberUOL.parse))
        self.assertEqual(Expression([n("123")]), Expression.parse_with(cpb("123 (456)"), NumberUOL.parse))
        self.assertEqual(Expression([n("123")]), Expression.parse_with(cpb(" 123"), NumberUOL.parse))
        self.assertEqual(Expression([n("-123")]), Expression.parse_with(cpb("-123"), NumberUOL.parse))
        self.assertEqual(Expression([n("123.45")]), Expression.parse_with(cpb("123.45"), NumberUOL.parse))
        self.assertEqual(Expression([nmm("123.45")]), Expression.parse_with(cpb("123.45mm "), NumberUOL.parse))
        self.assertEqual(
            Expression([n("123"), o("+"), n("456")]), Expression.parse_with(cpb("123+456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("456")]), Expression.parse_with(cpb("123 +456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("456")]), Expression.parse_with(cpb("123+ 456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("456")]), Expression.parse_with(cpb("123 + 456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("-"), n("456")]), Expression.parse_with(cpb("123-456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("-"), n("456")]), Expression.parse_with(cpb("123 -456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("-"), n("456")]), Expression.parse_with(cpb("123- 456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("-"), n("456")]), Expression.parse_with(cpb("123 - 456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("-456")]), Expression.parse_with(cpb("123+-456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("-456")]), Expression.parse_with(cpb("123 +-456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("-456")]), Expression.parse_with(cpb("123+ -456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("-456")]), Expression.parse_with(cpb("123 + -456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([nmm("123"), o("+"), n("-456")]), Expression.parse_with(cpb("123mm + -456"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([nmm("123"), o("+"), nmm("-456")]), Expression.parse_with(cpb("123mm + -456mm"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), nmm("-456")]), Expression.parse_with(cpb("123 + -456mm"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("456"), o("+"), n("789")]),
            Expression.parse_with(cpb("123+456+789"), NumberUOL.parse),
        )
        self.assertEqual(
            Expression([n("123"), o("+"), n("456"), o("+"), n("789")]),
            Expression.parse_with(cpb("123 +456 + 789"), NumberUOL.parse),
        )
        self.assertEqual(Expression([ob, n("123"), cb]), Expression.parse_with(cpb("(123)"), NumberUOL.parse))
        self.assertEqual(Expression([ob, n("123"), cb]), Expression.parse_with(cpb("(123)(456)"), NumberUOL.parse))
        self.assertEqual(Expression([ob, ob, n("123"), cb, cb]), Expression.parse_with(cpb("((123))"), NumberUOL.parse))
        self.assertEqual(
            Expression([ob, ob, n("123"), cb, cb]), Expression.parse_with(cpb("( (123 ))"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([ob, ob, n("123"), cb, cb]), Expression.parse_with(cpb("(( 123) )"), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([ob, ob, n("123"), cb, cb]), Expression.parse_with(cpb(" ( ( 123) ) "), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([ob, ob, n("123"), cb, cb]), Expression.parse_with(cpb(" ( ( 123 ) ) "), NumberUOL.parse)
        )
        self.assertEqual(
            Expression([ob, ob, n("123"), o("+"), n("456"), cb, cb]),
            Expression.parse_with(cpb(" ( ( 123+456 ) ) "), NumberUOL.parse),
        )
        self.assertEqual(
            Expression([ob, ob, n("123"), o("+"), n("456"), cb, cb]),
            Expression.parse_with(cpb(" ( ( 123 + 456 ) ) "), NumberUOL.parse),
        )
        self.assertEqual(
            Expression([ob, ob, n("123"), o("+"), ob, n("456"), o("-"), n("3"), cb, cb, cb]),
            Expression.parse_with(cpb(" ( ( 123 + (456-3) ) ) "), NumberUOL.parse),
        )
        self.assertEqual(
            Expression([ob, n("123"), o("+"), n("456"), cb, o("*"), n("789")]),
            Expression.parse_with(cpb("(123+456)*789"), NumberUOL.parse),
        )
        self.assertEqual(
            Expression([n("123"), o("*"), ob, n("789"), o("/"), n("3.14"), cb]),
            Expression.parse_with(cpb("123*(789/3.14)"), NumberUOL.parse),
        )
        self.assertEqual(
            Expression([ob, n("123"), cb, o("*"), ob, n("789"), o("/"), n("3.14"), cb]),
            Expression.parse_with(cpb("(123)*(789/3.14)"), NumberUOL.parse),
        )
        self.assertEqual(
            Expression([ob, n("123"), o("+"), n("456"), cb, o("*"), ob, n("789"), o("/"), n("3.14"), cb]),
            Expression.parse_with(cpb("(123+456)*(789/3.14)"), NumberUOL.parse),
        )

    def test_expression_invalid(self):
        self.assertIsNone(Expression.parse_with(cpb(""), NumberUOL.parse))
        self.assertIsNone(Expression.parse_with(cpb("123+"), NumberUOL.parse))
        self.assertIsNone(Expression.parse_with(cpb("123 +"), NumberUOL.parse))
        self.assertIsNone(Expression.parse_with(cpb("123 + "), NumberUOL.parse))
        self.assertIsNone(Expression.parse_with(cpb("- 123"), NumberUOL.parse))
        self.assertIsNone(Expression.parse_with(cpb("123 + - 1"), NumberUOL.parse))
        self.assertIsNone(Expression.parse_with(cpb("(123"), NumberUOL.parse))
        self.assertIsNone(Expression.parse_with(cpb("123 456"), NumberUOL.parse))

    def test_expression_invalid_with_uoa(self):
        self.assertIsNone(Expression.parse_with(cpb(""), NumberUOA.parse))
        self.assertIsNone(Expression.parse_with(cpb("123+"), NumberUOA.parse))
        self.assertIsNone(Expression.parse_with(cpb("123 +"), NumberUOA.parse))
        self.assertIsNone(Expression.parse_with(cpb("123 + "), NumberUOA.parse))
        self.assertIsNone(Expression.parse_with(cpb("- 123"), NumberUOA.parse))
        self.assertIsNone(Expression.parse_with(cpb("123 + - 1"), NumberUOA.parse))
        self.assertIsNone(Expression.parse_with(cpb("(123"), NumberUOA.parse))
        self.assertIsNone(Expression.parse_with(cpb("123 456"), NumberUOA.parse))

    def test_computation_valid(self):
        # Helper functions
        def n(n_str, u=None):
            return NumberUOL(n_str, u)

        def o(o_str):
            return Operator(o_str)

        def c(left, operator, right):
            return Computation(left, operator, right)

        self.assertEqual(c(n("123"), o("+"), n("0")), Computation.parse_with(cpb("123"), NumberUOL.parse))
        self.assertEqual(c(n("123"), o("+"), n("0")), Computation.parse_with(cpb("(123)"), NumberUOL.parse))
        self.assertEqual(
            c(n("123"), o("+"), n("0")), Computation.parse_with(cpb(" (  ( ( 123)  ) )  "), NumberUOL.parse)
        )
        self.assertEqual(c(n("123"), o("+"), n("0")), Computation.parse_with(cpb("(((123)))"), NumberUOL.parse))

        self.assertEqual(c(n("123"), o("+"), n("456")), Computation.parse_with(cpb("123+456"), NumberUOL.parse))
        self.assertEqual(
            c(c(n("123"), o("+"), n("456")), o("-"), n("789")),
            Computation.parse_with(cpb("123+456-789"), NumberUOL.parse),
        )
        self.assertEqual(
            c(n("123"), o("+"), c(n("456"), o("*"), n("789"))),
            Computation.parse_with(cpb("123+456*789"), NumberUOL.parse),
        )
        self.assertEqual(
            c(c(n("123"), o("/"), n("456")), o("-"), n("789")),
            Computation.parse_with(cpb("123/456-789"), NumberUOL.parse),
        )
        self.assertEqual(
            c(c(c(n("1"), o("+"), n("2")), o("*"), n("3")), o("-"), n("4")),
            Computation.parse_with(cpb("(1+2)*3-4"), NumberUOL.parse),
        )
        self.assertEqual(
            c(c(n("1"), o("+"), n("2")), o("/"), c(n("3"), o("-"), n("4"))),
            Computation.parse_with(cpb("(1+2)/(3-4)"), NumberUOL.parse),
        )
        self.assertEqual(
            c(
                n("1"),
                o("+"),
                c(n("2"), o("/"), c(n("3"), o("-"), n("4"))),
            ),
            Computation.parse_with(cpb("1+2/(3-4)"), NumberUOL.parse),
        )
        self.assertEqual(
            c(
                c(n("1"), o("+"), c(n("2"), o("/"), n("3"))),
                o("-"),
                n("4"),
            ),
            Computation.parse_with(cpb("1+2/3-4"), NumberUOL.parse),
        )
        self.assertEqual(
            c(
                n("1"),
                o("+"),
                c(n("2"), o("/"), c(n("3"), o("-"), c(n("4"), o("+"), n("5")))),
            ),
            Computation.parse_with(cpb("1+2/(3-(4+5))"), NumberUOL.parse),
        )
        self.assertEqual(
            c(
                n("1"),
                o("+"),
                c(n("2"), o("/"), c(c(n("3"), o("-"), n("4")), o("+"), n("5"))),
            ),
            Computation.parse_with(cpb("1+2/((3-4)+5)"), NumberUOL.parse),
        )

        # Test compute method
        comp = Computation.parse_with(cpb("1"), NumberUOL.parse)
        self.assertIsNotNone(comp)
        self.assertEqual(1, comp.compute(UnitOfLength.Centimeter))  # type: ignore

        self.assertEqual(2, Computation.parse_with(cpb("2"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertEqual(2, Computation.parse_with(cpb("(2)"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertAlmostEqual(3.14, Computation.parse_with(cpb("3.14"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertEqual(2, Computation.parse_with(cpb("1+1"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertEqual(3, Computation.parse_with(cpb("1cm+2cm"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertAlmostEqual(4.14, Computation.parse_with(cpb("1cm+3.14cm"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertAlmostEqual(4.14, Computation.parse_with(cpb("1cm+31.4mm"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertAlmostEqual(4.14, Computation.parse_with(cpb("10mm+31.4mm"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertAlmostEqual(4.14 / 100, Computation.parse_with(cpb("10mm+31.4mm"), NumberUOL.parse).compute(UnitOfLength.Meter))  # type: ignore
        self.assertAlmostEqual(4.14 / 100, Computation.parse_with(cpb("1m/100+31.4mm"), NumberUOL.parse).compute(UnitOfLength.Meter))  # type: ignore
        self.assertAlmostEqual(4.14, Computation.parse_with(cpb("1m/100+31.4mm"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore

        self.assertAlmostEqual(-3, Computation.parse_with(cpb("(1+2)/(3-4)"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertAlmostEqual(-3, Computation.parse_with(cpb("(1+2)/3-4"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertAlmostEqual(-1, Computation.parse_with(cpb("1+2/(3-4)"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore
        self.assertAlmostEqual(-2.33333, Computation.parse_with(cpb("1+2/3-4"), NumberUOL.parse).compute(UnitOfLength.Centimeter), places=5)  # type: ignore
        self.assertAlmostEqual(0.66667, Computation.parse_with(cpb("1+2/(3-(4+5))"), NumberUOL.parse).compute(UnitOfLength.Centimeter), places=5)  # type: ignore
        self.assertAlmostEqual(1.5, Computation.parse_with(cpb("1+2/((3-4)+5)"), NumberUOL.parse).compute(UnitOfLength.Centimeter))  # type: ignore


if __name__ == "__main__":
    unittest.main()
