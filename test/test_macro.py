import unittest
import ctypes

from ctypeslib.codegen.util import get_cursor
from ctypeslib.codegen.util import get_tu
from util import ClangTest

'''Test if macro are correctly generated.
'''


class Macro(ClangTest):
    # @unittest.skip('')

    def setUp(self):
        # we need to generate macro. Which is very long for some reasons.
        self.full_parsing_options = True

    def test_simple_integer_literal(self):
        self.convert('''#define MY_VAL 1''')
        self.assertEqual(self.namespace.MY_VAL, 1)
        self.convert('''#define __MY_VAL 1''')
        self.assertEqual(getattr(self.namespace, "__MY_VAL"), 1)

    def test_char_arrays(self):
        self.convert('''
#define PRE "before"
#define POST " after"
#define APREPOST PRE POST

char a[] = "what";
char b[] = "why" " though";
char c[] = PRE POST;
char d[] = APREPOST;''')
        self.assertEqual(self.namespace.a, "what")
        self.assertEqual(self.namespace.b, "why though")
        self.assertEqual(self.namespace.c, 'before after')
        self.assertEqual(self.namespace.d, 'before after')
        print(self.text_output)

    def test_long(self):
        self.convert('''#define BIG_NUM_L 1000000L''')
        self.assertEqual(getattr(self.namespace, "BIG_NUM_L"), 1000000)

    def test_unsigned_long_long(self):
        self.convert('''#define BIG_NUM_ULL 0x0000000080000000ULL''')
        self.assertEqual(getattr(self.namespace, "BIG_NUM_ULL"), 0x0000000080000000)

    def test_simple_replace_typedef(self):
        """When macro are used as typedef, it's transparent to us. """
        # Python does not have typedef so who care what type name is a variable ?
        self.convert('''
            #define macro_type int
            macro_type i = 10;
            ''')
        # macro_type = int # macro
        # i = 10 # Variable ctypes.c_int32
        # very little
        self.assertIn("i", self.namespace)
        self.assertEqual(self.namespace.i, 10)
        print(self.text_output)

    def test_simple_replace_function(self):
        """When macro are used as typedef, it's transparent to us. """
        # Python does not have typedef so who care what type name is a variable ?
        self.convert('''
            #define macro_type int
            macro_type fn(int a, int b) {return a+b} ;
            ''', )
        # macro_type = int # macro
        # i = 10 # Variable ctypes.c_int32
        # very little
        print(self.text_output)
        self.assertIn("fn", self.namespace)
        # self.assertIn("fn", self.text_output)
        # self.assertEqual(self.namespace.i, 10)

    def test_function(self):
        self.convert('''
#define fn_type void
#define fn_name(a,b) real_name(a,b)
fn_type fn_name(int a, int b);
''')
        self.assertIn("real_name", self.namespace)

    def test_simple_macro_function(self):
        self.convert('''
    #define HI(x) x
    HI(int) y;
    ''')
        # print(self.text_output)
        self.assertIn("y", self.namespace)
        self.assertEqual(self.namespace.y, 0)
        self.assertIn("HI", self.text_output)
        # only comments for functions
        self.assertNotIn("HI", self.namespace)


    def test_example(self):
        self.convert('''
#define DEBUG
#define PROD 1
#define MACRO_EXAMPLE(x,y) {x,y}
#define MY 1 2 3 4 5 6

int tab1[] = MACRO_EXAMPLE(1,2); 
''')
        self.assertIn("tab1", self.namespace)
        self.assertEqual(self.namespace.tab1, [1, 2])
        self.assertEqual(self.namespace.DEBUG, True)
        self.assertEqual(self.namespace.PROD, 1)
        # we don't gen macro functions
        self.assertNotIn('MACRO_EXAMPLE', self.namespace)
        # print(self.text_output)

    # L"string" not supported
    # -1 literal is split as ['-','1']
    @unittest.expectedFailure
    def test_defines(self):
        # we need macros
        self.full_parsing_options = True
        self.convert("""
        #define zero 0
        #define one 1
        #define minusone -1
        #define maxint 2147483647
        #define minint -2147483648
        #define spam "spam"
        #define foo L"foo"
        #define LARGE 0xFFFFFFFF

        #ifdef _MSC_VER
        # define VERYLARGE 0xFFFFFFFFFFFFFFFFui64
        #endif
        """)

        self.assertEqual(self.namespace.zero, 0)
        self.assertEqual(self.namespace.one, 1)
        self.assertEqual(self.namespace.minusone, -1)
        self.assertEqual(self.namespace.maxint, 2147483647)
        self.assertEqual(self.namespace.LARGE, 0xFFFFFFFF)
        ##        self.assertEqual(self.namespace.VERYLARGE, 0xFFFFFFFFFFFFFFFF)
        ##        self.assertEqual(self.namespace.minint, -2147483648)

        self.assertEqual(self.namespace.spam, "spam")
        self.assertEqual(type(self.namespace.spam), str)

        self.assertEqual(self.namespace.foo, "foo")
        self.assertEqual(type(self.namespace.foo), unicode)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
