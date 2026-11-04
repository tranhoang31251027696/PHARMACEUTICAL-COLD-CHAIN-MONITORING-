; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x2473 (ite (>= 17.0 (* alpha 18.0)) 54 (ite (>= 1.0 (* alpha 1.0)) 49 0))))
(let ((?x1588 (ite (>= 51.0 (* alpha 56.0)) 56 (ite (>= 51.0 (* alpha 55.0)) 55 ?x2473))))
(let ((?x3879 (ite (>= 51.0 (* alpha 58.0)) 58 (ite (>= 17.0 (* alpha 19.0)) 57 ?x1588))))
(let ((?x894 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 52.0 (* alpha 67.0)) 67 ?x3879))))
(and (distinct ?x894 ?x894) true))))))
(check-sat)
