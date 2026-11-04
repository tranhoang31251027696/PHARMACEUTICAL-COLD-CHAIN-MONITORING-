; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x2138 (ite (>= 51.0 (* alpha 52.0)) 52 (ite (>= 1.0 (* alpha 1.0)) 47 0))))
(let ((?x287 (ite (>= 51.0 (* alpha 59.0)) 59 (ite (>= 51.0 (* alpha 56.0)) 56 ?x2138))))
(let ((?x4216 (ite (>= 53.0 (* alpha 143.0)) 143 ?x287)))
(and (distinct ?x4216 ?x4216) true)))))
(check-sat)
