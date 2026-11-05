//Demo: declare a DFA that accepts strings ending in 0.
dfa EndsWithZero {
    states: s0, s1
    alphabet: "0", "1"
    start: s0
    accept: s1
    transitions: {
        s0 -> s1: "0"
        s0 -> s0: "1"
        s1 -> s1: "0"
        s1 -> s0: "1"
    }
}

//Demo: a regular expression for strings containing an odd number of 1s.
regex HasOddOnes = ("0"* "1" "0"* "1" "0"*)* "0"* "1" "0"*
