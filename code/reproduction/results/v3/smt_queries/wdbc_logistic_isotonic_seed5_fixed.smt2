; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x553 (ite (>= 51.0 (* alpha 56.0)) 56 (ite (>= 51.0 (* alpha 55.0)) 55 0))))
(let ((?x1342 (ite (>= 51.0 (* alpha 58.0)) 58 (ite (>= 17.0 (* alpha 19.0)) 57 ?x553))))
(let ((?x1959 (ite (>= 53.0 (* alpha 143.0)) 143 ?x1342)))
(and (distinct ?x1959 ?x1959) true)))))
(check-sat)
