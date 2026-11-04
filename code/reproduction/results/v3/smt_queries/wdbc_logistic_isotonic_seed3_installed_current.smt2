; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x894 (>= 1.0 (* alpha 1.0))))
(let ((?x3726 (ite (>= 53.0 (* alpha 55.0)) 55 (ite $x894 50 (ite $x894 49 (ite $x894 48 0))))))
(let ((?x2156 (ite (>= 53.0 (* alpha 79.0)) 79 (ite (>= 53.0 (* alpha 57.0)) 57 ?x3726))))
(let ((?x4180 (ite (>= 53.0 (* alpha 81.0)) 81 (ite (>= 53.0 (* alpha 80.0)) 80 ?x2156))))
(let ((?x2360 (ite (>= 53.0 (* alpha 83.0)) 83 (ite (>= 53.0 (* alpha 82.0)) 82 ?x4180))))
(let ((?x3295 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 53.0 (* alpha 84.0)) 84 ?x2360))))
(and (distinct ?x3295 ?x3295) true))))))))
(check-sat)
