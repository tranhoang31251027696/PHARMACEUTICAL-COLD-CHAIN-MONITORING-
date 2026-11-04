; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x79 (ite (>= 51.0 (* alpha 52.0)) 52 (ite (>= 1.0 (* alpha 1.0)) 47 0))))
(let ((?x4216 (ite (>= 51.0 (* alpha 59.0)) 59 (ite (>= 51.0 (* alpha 56.0)) 56 ?x79))))
(let ((?x2764 (ite (>= 53.0 (* alpha 143.0)) 143 ?x4216)))
(and (distinct ?x2764 ?x2764) true)))))
(check-sat)
