; *******************************************************************************************
; *******************************************************************************************
;
;       File:           muldiv.asm
;       Date:           14th November 2020
;       Purpose:        Multiply and Divide and Modulus routines for 6502 code.
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************
;
;		These routines allow you to code in 6502
;
;			jsr MultiplyImmediate 					; multiply XA by 42
;			.word 42
;
;		and
; 			
;			jsr MultiplyAbsolute 					; multiply XA by the word at $20E7
;			.word $20E7
;
; *******************************************************************************************
;
;	Currently provided for Multiply, Divide and Modulus, and String Constant.
;
; *******************************************************************************************


; *******************************************************************************************
;
;										String Accessor
;
; *******************************************************************************************

		define 	"string.constant",EndStringConstant
StringConstant:
		pla 										; pull address and save in temp0
		sta 	temp0
		pla 
		sta 	temp0+1
		inc16 	temp0 								; temp0 now points to the string.
		ldy 	#0 									; figure out the end of the string.
_SCEnd:	lda 	(temp0),y
		iny
		cmp 	#0
		bne 	_SCEnd
		;
		clc 										; add Y to temp0, to continue, while putting
		sty 	temp1 								; original value into XY

		clc
		lda 	temp0 								
		tay
		adc 	temp1
		sta 	temp0
		lda 	temp0+1
		tax
		adc 	#0
		sta 	temp0+1
		;
		tya 										; value now in XA
		jmp 	(temp0)								; and continue.

EndStringConstant:

; *******************************************************************************************
;
;									  Arithmetic support
;
; *******************************************************************************************

		define 	"multiply.immediate",EndMultiplyImmediate
MultiplyImmediate:	
		jsr 	SaveXTemp1GetTemp0
		jsr 	Multiply
		lda 	Reg16
		ldx 	Reg16+1
		rts
EndMultiplyImmediate:

		define 	"multiply.absolute",EndMultiplyAbsolute
MultiplyAbsolute:
		jsr 	SaveXTemp1GetTemp0
		jsr 	LoadIndirectTemp0
		jsr 	Multiply
		lda 	Reg16
		ldx 	Reg16+1
		rts
EndMultiplyAbsolute:


		define 	"divide.immediate",EndDivideImmediate
DivideImmediate:
		jsr 	SaveXTemp1GetTemp0
		jsr 	Divide
		lda 	temp1
		ldx 	temp1+1
		rts
EndDivideImmediate:

		define 	"divide.absolute",EndDivideAbsolute
DivideAbsolute:
		jsr 	SaveXTemp1GetTemp0
		jsr 	LoadIndirectTemp0
		jsr 	Divide
		lda 	temp1
		ldx 	temp1+1
		rts
EndDivideAbsolute:

		define 	"modulus.immediate",EndModulusImmediate
ModulusImmediate:
		jsr 	SaveXTemp1GetTemp0
		jsr 	Divide
		lda 	Reg16
		ldx 	Reg16+1
		rts
EndModulusImmediate:

		define 	"modulus.absolute",EndMulDivContent
ModulusAbsolute:
		jsr 	SaveXTemp1GetTemp0
		jsr 	LoadIndirectTemp0
		jsr 	Divide
		lda 	Reg16
		ldx 	Reg16+1
		rts

; *******************************************************************************************
;
;		Save XA in temp1, extract the word following the call as a value into temp0
;
; *******************************************************************************************

SaveXTemp1GetTemp0:
		sta 	temp1 						; write XA out.
		stx 	temp1+1
		tsx 								; get stack pointer so we can access return two up.

		clc 								; copy the address to temp0, adding 2 and updating.
		lda 	$0103,x 					
		sta 	temp0
		adc 	#2
		sta 	$0103,x
		lda 	$0104,x
		sta 	temp0+1
		adc 	#0
		sta 	$0104,x

		ldy 	#1 							; temp0 points to high byte of call, rts works that way
		lda 	(temp0),y 					; so get the word there.
		tax
		iny
		lda 	(temp0),y
		sta 	temp0+1
		stx 	temp0
		rts

; *******************************************************************************************
;
;		Load the 16 bit word at temp0 into temp0
;
; *******************************************************************************************

LoadIndirectTemp0:
		ldy 	#0							; low byte into X
		lda 	(temp0),y
		tax
		iny
		lda 	(temp0),y 					; high byte into A
		sta 	temp0+1 					; copy out.
		stx 	temp0
		rts

; *******************************************************************************************
;
;		Harness to test external functions.
;
; *******************************************************************************************

		.if test==2
TestExternal:
		jsr 	StringConstant
		.text 	"HELLO,WORLD!",0
		ldy 	#$DD
		debug
		.endif

EndMulDivContent:
