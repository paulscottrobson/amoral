; *******************************************************************************************
; *******************************************************************************************
;
;       File:           multiply.asm
;       Date:           14th November 2020
;       Purpose:        Multiply code
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;								Handles Multiply
;
; *******************************************************************************************

MultiplyHandler:	;; MLT $86
		jsr 	EvaluateValue 				; temp0 = target value.
		lda 	Reg16 						; temp1 = reg16
		sta 	temp1
		lda	 	Reg16+1
		sta 	temp1+1
		jsr 	Multiply 					; Reg16 := temp0 * temp1
		jmp 	ExecLoop

; *******************************************************************************************
;
;								Reg16 := temp0 * temp1
;
; *******************************************************************************************

Multiply:
		lda 	#0 							; zero total.
		sta 	Reg16
		sta 	Reg16+1
_MultLoop:
		lsr 	temp0+1
		ror 	temp0	
		bcc 	_MultNoAdd
		clc
		lda 	temp1		
		adc 	Reg16
		sta 	Reg16
		lda 	temp1+1
		adc 	Reg16+1
		sta 	Reg16+1
_MultNoAdd:
		asl 	temp1
		rol 	temp1+1
		lda 	temp0
		ora 	temp0+1
		bne 	_MultLoop
		rts
