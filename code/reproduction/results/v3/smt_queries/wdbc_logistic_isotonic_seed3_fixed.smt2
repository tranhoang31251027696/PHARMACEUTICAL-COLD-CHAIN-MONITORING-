; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x1959 (>= 1.0 (* alpha 1.0))))
(let ((?x3563 (ite (>= 53.0 (* alpha 55.0)) 55 (ite $x1959 50 (ite $x1959 49 (ite $x1959 48 0))))))
(let ((?x3876 (ite (>= 53.0 (* alpha 79.0)) 79 (ite (>= 53.0 (* alpha 57.0)) 57 ?x3563))))
(let ((?x1588 (ite (>= 53.0 (* alpha 81.0)) 81 (ite (>= 53.0 (* alpha 80.0)) 80 ?x3876))))
(let ((?x593 (ite (>= 53.0 (* alpha 83.0)) 83 (ite (>= 53.0 (* alpha 82.0)) 82 ?x1588))))
(let ((?x2964 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 53.0 (* alpha 84.0)) 84 ?x593))))
(and (distinct ?x2964 ?x2964) true))))))))
(check-sat)
