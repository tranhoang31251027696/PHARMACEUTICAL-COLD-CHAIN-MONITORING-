; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x2138 (ite (>= 53.0 (* alpha 64.0)) 64 (ite (>= 1.0 (* alpha 1.0)) 49 0))))
(let ((?x3726 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 53.0 (* alpha 65.0)) 65 ?x2138))))
(and (distinct ?x3726 ?x3726) true))))
(check-sat)
