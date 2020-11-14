; *******************************************************************************************
; *******************************************************************************************
;
;       File:           branches.asm
;       Date:           14th November 2020
;       Purpose:        Branch handlers
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;									Unconditional Branch
;
; *******************************************************************************************

Branch_Always: 	;; BRA 	$8B
		ldy 	#0
		lda 	(Pctr),y
		tax
		iny
		lda 	(Pctr),y
		sta 	Pctr+1
		stx 	Pctr
		jmp 	ExecLoop

; *******************************************************************************************
;
;										Branch Conditional
;
; *******************************************************************************************

Branch_Zero: 	;; BEQ $8C
		lda 	Reg16
		ora 	Reg16+1
		beq 	Branch_Always
		bne 	Branch_Fail

Branch_NonZero: 	;; BNE $8D
		lda 	Reg16
		ora 	Reg16+1
		bne 	Branch_Always
Branch_Fail:
		clc
		lda 	Pctr
		adc 	#2
		sta 	Pctr
		bne 	_BFNoCarry
		inc 	Pctr+1
_BFNoCarry:
		jmp 	ExecLoop		

Branch_Minus:	;; BMI $8E
		lda 	Reg16+1
		bmi 	Branch_Always
		bpl 	Branch_Fail

Branch_Positive:	;; BPL $8F
		lda 	Reg16+1
		bpl 	Branch_Always
		bmi 	Branch_Fail
