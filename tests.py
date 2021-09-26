#Includes tests for the blog project
#TODO: Write tests for the web blog project
import pytest
def capital_case(x):
    return x.capitalize()

def test_capital_case():
    assert capital_case('blog') == 'Blog'
