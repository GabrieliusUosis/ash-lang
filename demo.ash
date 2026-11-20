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

dfa StartsWithB {
    states: s0, s1, s3
    alphabet: "a", "b"
    start: s0
    accept: s1
    transitions: {
        s0 -> s1: "b"
        s0 -> s3: "a"
        s1 -> s1: "a"
        s1 -> s1: "b"
        s3 -> s3: "a"
        s3 -> s3: "b"
    }
}

nfa EndsWith01 {
    states: q0, q1, q2
    alphabet: "0", "1"
    start: q0
    accept: q2
    transitions: {
        q0 -> q0: "0"
        q0 -> q0: "1"
        q0 -> q1: "0"
        q1 -> q2: "1"
    }
}

