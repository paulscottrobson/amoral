word vera.low@$9f20
byte vera.high@$9f22
byte vera.data@$9f23

word .sprite.base 				// current base address of sprite
byte .sprite.mode 				// 0=4bpp, $80=8 bpp

//
//		Set vera write address with +1 step (low,high)
//
proc vera.set()
	vera.low = R
	A=Y A&$0F A:$10 vera.high=A
endproc
//
//		Set palette (RGB,index)
//
proc vera.palette()
	RAY->S
	R->S R=Y <<R R:$1000 Y=$0F vera.set()
	S->R vera.data=A R.Swap vera.data=A
	S->RAY
endproc
//
//		Sprites on/off R
//
proc vera.sprites.enable()
	RAY->S .sprite.mode=Y R<>? if 1 endif A->S vera.set($4000,$F) S->A vera.data=A S->RAY
endproc
//
//		Set current active sprite to R
//
proc vera.select()
	RAY->S R&$7F <<A <<R <<R R:$5000 .sprite.base=R S->RAY
endproc
//
//		Set offset to R
//
proc .vera.access()
	Y->S R+.sprite.base Y=$0F vera.set() S->Y
endproc
//
//		Set sprite position to R
//
proc vera.x()
	RAY->S R->S .vera.access(2) S->R vera.data=A R.swap vera.data=A S->RAY
endproc
proc vera.y()
	RAY->S R->S .vera.access(4) S->R vera.data=A R.swap vera.data=A S->RAY
endproc
//
//		Initialise sprite with size in R
//
proc vera.create()
	RAY->S
	<<A <<A <<A <<A A->S
	.vera.access(6) A = 12 vera.data=A S->A vera.data=A
	S->RAY
endproc
//
//		Set sprite image. Address is 1/16th of actual, so R = $1800 
//		actually sets it to $18000, and it must be even. 
//
proc vera.graphic()
	RAY->S
	>>R R->S R->S .vera.access(0) 
	S->R vera.data=A
	S->R R.Swap A&$0F A+.sprite.mode vera.data=A
	S->RAY
endproc

word p@$10
word temp@$0E
word free.mem
byte count,current

proc balls.self()
	vera.select()
	<<A <<A R=A R+free.mem p=R
endproc

proc ball.getx() y=0 R=p[y] endproc
proc ball.setx() y=0 p[y]=R endproc
proc ball.getxi() y=2 R=p[y] endproc
proc ball.setxi() y=2 p[y]=R endproc

proc xi.flip()
	.vera.access(6)
	ball.getxi() -R ball.setxi()
	R-? if A=13 else A=12 endif vera.data=A
endproc

proc times.16() 
	<<R <<R <<R <<R
endproc

proc main()
	free.mem = R 
	A=24 count=A
	vera.sprites.enable(1,0)
	A=count a.for
		current=A balls.self(current)
		ball.setx(32)
		R=current ++R ball.setxi()
		vera.create($0F)
		vera.graphic($1000)
		R=current times.16() vera.y()
	next

	10000 r.for
		A=count a.for
			current = A 
			balls.self()
			ball.getx() vera.x() temp=R
			ball.getxi() R+temp ball.setx()
			R>=608? if xi.flip() endif
			200 r.for next
		next
	next
endproc

remove.locals
