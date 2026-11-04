; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x3726 (ite (>= 13.0 (* alpha 18.0)) 72 (ite (>= 51.0 (* alpha 53.0)) 53 0))))
(let ((?x1342 (ite (>= 26.0 (* alpha 37.0)) 74 (ite (>= 52.0 (* alpha 73.0)) 73 ?x3726))))
(let ((?x1324 (ite (>= 53.0 (* alpha 143.0)) 143 ?x1342)))
(and (distinct ?x1324 ?x1324) true)))))
(check-sat)
