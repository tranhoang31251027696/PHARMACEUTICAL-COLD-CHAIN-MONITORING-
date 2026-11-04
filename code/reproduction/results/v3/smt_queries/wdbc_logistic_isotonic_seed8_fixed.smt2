; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x4216 (ite (>= 53.0 (* alpha 64.0)) 64 (ite (>= 1.0 (* alpha 1.0)) 49 0))))
(let ((?x389 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 53.0 (* alpha 65.0)) 65 ?x4216))))
(and (distinct ?x389 ?x389) true))))
(check-sat)
