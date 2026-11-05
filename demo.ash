// DFA 1: Accepts binary strings ending in "0"
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

// DFA 2: Accepts binary strings containing an even number of "0"s
dfa EvenZeros {
    states: q_even, q_odd
    alphabet: "0", "1"
    start: q_even
    accept: q_even
    transitions: {
        q_even -> q_odd: "0"
        q_even -> q_even: "1"
        q_odd -> q_even: "0"
        q_odd -> q_odd: "1"
    }
}

// DFA 3: Accepts strings over {"a", "b"} containing the substring "ab"
dfa ContainsAB {
    states: q0, q1, q2
    alphabet: "a", "b"
    start: q0
    accept: q2
    transitions: {
        q0 -> q1: "a"
        q0 -> q0: "b"
        q1 -> q1: "a"
        q1 -> q2: "b"
        q2 -> q2: "a"
        q2 -> q2: "b"
    }
}

// DFA 4: Accepts binary numbers divisible by 3 (states track remainder mod 3)
dfa DivisibleByThree {
    states: r0, r1, r2
    alphabet: "0", "1"
    start: r0
    accept: r0
    transitions: {
        r0 -> r0: "0"
        r0 -> r1: "1"
        r1 -> r2: "0"
        r1 -> r0: "1"
        r2 -> r1: "0"
        r2 -> r2: "1"
    }
}

// Regex: Strings containing an odd number of 1s
regex HasOddOnes = ("0"* "1" "0"* "1" "0"*)* "0"* "1" "0"*
