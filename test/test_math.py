import math

def test_shouldBePrime():
    assert math.is_prime(7) == True

def test_shouldNotBePrime():
    assert math.is_prime(55) == False
