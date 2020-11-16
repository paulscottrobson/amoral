; *******************************************************************************************
; *******************************************************************************************
;
;       File:           utility2.asm
;       Date:           16th November 2020
;       Purpose:        More Utility routines for 6502 code.
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;							Minimum/Maximum of 2 values (unsigned)
;
; *******************************************************************************************

		define 	"max:2",EndMax
		tay 								; save in Y
		cmp 	Param1 						; compare XA vs param1
		txa
		sbc 	Param1+1
		tya 								; ready to return original value.
		bcc 	MMReturnP1
		rts
MMReturnP1:
		lda 	Param1
		ldx 	Param1+1
		rts				
EndMax:

		define 	"min:2",EndMin
		tay 								; save in Y
		cmp 	Param1 						; compare XA vs param1
		txa
		sbc 	Param1+1
		tya 								; ready to return original value.
		bcs 	MMReturnP1
		rts
EndMin:

; *******************************************************************************************
;
;											Abs
;
; *******************************************************************************************

		define 	"abs:1",EndAbs
		cpx 	#0
		bmi 	Negate
		rts
EndAbs:

; *******************************************************************************************
;
;										Negate XA
;
; *******************************************************************************************

		define 	"neg:1",EndNegate
Negate:	pha
		txa
		eor 	#$FF
		tax
		pla
		eor 	#$FF
		clc
		adc 	#1
		bcc 	_NGExit
		inx
_NGExit:rts
EndNegate:				

; *******************************************************************************************
;
;											Sgn
;
; *******************************************************************************************

		define 	"sgn:1",EndSgn
		ldy 	#$FF
		cpx 	#0
		bmi 	_SGRetYA
		bne 	_SGPositive
		iny
		cmp 	#0
		bne 	_SGPositive
_SGRetYA:
		tya
		tax
		rts
_SGPositive:		
		lda 	#1
		ldx 	#0
		rts
EndSgn:

; *******************************************************************************************
;
;									  Length of string
;
; *******************************************************************************************

		define "len:1",EndLen
		sta 	temp0
		stx 	temp0+1
		ldy 	#255
_GetLen:iny
		lda 	(temp0),y
		bne 	_GetLen
		tax
		tya
		rts
EndLen:

; *******************************************************************************************
;
;									 Allocate memory
;
; *******************************************************************************************

		define "alloc:1",EndAlloc
		tay 								; XY is size.
		lda 	AllocMem 					; push allocated addr on stack
		pha
		lda 	AllocMem+1
		pha
		;
		clc 								; add XY to alloc mem
		tya
		adc 	AllocMem
		sta 	AllocMem
		txa
		adc 	AllocMem+1
		sta 	AllocMem+1
		;
		pla 								; restore and exit
		tax
		pla
		rts
EndAlloc:

; *******************************************************************************************
;
;									Random number 16 bit
;
; *******************************************************************************************

		define 	"random:0",EndRandom
		lda 	RandomSeed 					; initialise if nonzero
		ora 	RandomSeed+1
		bne 	_R16_NoInit
		lda 	#$A3
		sta 	RandomSeed
		lda 	#$75
		sta 	RandomSeed+1
_R16_NoInit:
		lsr 	RandomSeed+1				; shift seed right
		ror 	RandomSeed
		bcc 	_R16_NoXor
		lda 	RandomSeed+1				; xor MSB with $B4 if bit set.
		eor 	#$B4 						; like the Wikipedia one.
		sta 	RandomSeed+1
_R16_NoXor:				
		lda 	RandomSeed					; copy result to evaluate stack.
		ldx 	RandomSeed+1
		rts
EndRandom		