def audit_run(run_dir: str):
    '''Distribute documents to the annotators with some of the documents overlapping, this is,
    some specific documents are present in more than one annotator.'''

    docs = get_filenames()

    # Initialize the list for each annotator
    A = list()
    B = list()
    C = list()
    D = list()

    # First annotator (A)
    A.extend(docs[:audit_bunch])

    # Second annotator (B)
    # Append to B only the two first overlapping docs from A
    [B.append(A[i]) for i in OVERLAPPINGS.get('A')[:2]]
    B.extend(docs[audit_bunch:(audit_bunch * 2) - 2])

    # Third annotator (C)
    C.extend(docs[(audit_bunch * 2) - 2: audit_bunch * 3][:2])
    # Append to C all the defined overlapping docs from B
    [C.append(B[i]) for i in OVERLAPPINGS.get('B')]
    C.extend(docs[audit_bunch * 2:(audit_bunch * 3) - 4])

    # Fourth annotator (D)
    D.extend(docs[(audit_bunch * 3) - 4: audit_bunch * 4][:3])
    D.append(B[3])
    # Append to D all the defined overlapping docs from C
    [D.append(C[i]) for i in OVERLAPPINGS.get('C')]
    # Append to D only the three last overlapping docs from A
    [D.append(A[i]) for i in OVERLAPPINGS.get('A')[2:]]
    D.extend(docs[(audit_bunch * 3) - 1:(audit_bunch * 4 - 10)])

    audit_run = {
        'A': A,
        'B': B,
        'C': C,
        'D': D
    }

    return audit_run
