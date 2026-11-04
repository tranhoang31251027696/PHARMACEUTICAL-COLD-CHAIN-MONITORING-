; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x503 (>= 1.0 (* alpha 1.0))))
(let ((?x593 (ite (>= 50.0 (* alpha 51.0)) 51 (ite $x503 50 (ite $x503 49 (ite $x503 48 0))))))
(let ((?x4100 (ite (>= 51.0 (* alpha 53.0)) 53 (ite (>= 25.0 (* alpha 26.0)) 52 ?x593))))
(let ((?x4216 (ite (>= 51.0 (* alpha 55.0)) 55 (ite (>= 17.0 (* alpha 18.0)) 54 ?x4100))))
(let ((?x4180 (ite (>= 17.0 (* alpha 19.0)) 57 (ite (>= 51.0 (* alpha 56.0)) 56 ?x4216))))
(let ((?x79 (ite (>= 53.0 (* alpha 75.0)) 75 (ite (>= 53.0 (* alpha 74.0)) 74 ?x4180))))
(let ((?x1586 (ite (>= 53.0 (* alpha 83.0)) 83 (ite (>= 53.0 (* alpha 82.0)) 82 ?x79))))
(let ((?x678 (ite (>= 53.0 (* alpha 143.0)) 143 ?x1586)))
(and (distinct ?x678 ?x678) true))))))))))
(check-sat)
