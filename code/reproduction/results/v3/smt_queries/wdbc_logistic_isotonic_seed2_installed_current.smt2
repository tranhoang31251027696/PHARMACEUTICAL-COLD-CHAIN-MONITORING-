; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x923 (>= 1.0 (* alpha 1.0))))
(let ((?x741 (ite $x923 51 (ite $x923 50 (ite $x923 49 (ite $x923 48 0))))))
(let ((?x92 (ite (>= 13.0 (* alpha 16.0)) 64 (ite (>= 51.0 (* alpha 52.0)) 52 ?x741))))
(let ((?x4352 (ite (>= 53.0 (* alpha 143.0)) 143 ?x92)))
(and (distinct ?x4352 ?x4352) true))))))
(check-sat)
