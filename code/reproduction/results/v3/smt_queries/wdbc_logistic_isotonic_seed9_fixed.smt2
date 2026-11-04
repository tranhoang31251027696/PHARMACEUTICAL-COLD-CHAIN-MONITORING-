; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x3876 (ite (>= 51.0 (* alpha 52.0)) 52 (ite (>= 1.0 (* alpha 1.0)) 47 0))))
(let ((?x1363 (ite (>= 51.0 (* alpha 59.0)) 59 (ite (>= 51.0 (* alpha 56.0)) 56 ?x3876))))
(let ((?x1166 (ite (>= 53.0 (* alpha 143.0)) 143 ?x1363)))
(and (distinct ?x1166 ?x1166) true)))))
(check-sat)
