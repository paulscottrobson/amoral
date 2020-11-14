; *******************************************************************************************
; *******************************************************************************************
;
;       File:           divide.asm
;       Date:           14th November 2020
;       Purpose:        Divide and Modulus code
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;								Handles Divide
;
; *******************************************************************************************

DivideHandler:	;; DIV $87
		jsr 	EvaluateValue 				; temp0 = target value.
		lda 	Reg16 						; temp1 = reg16
		sta 	temp1
		lda	 	Reg16+1
		sta 	temp1+1
		jsr 	Divide 						; temp1 := temp1 / temp0
		lda 	temp1 						; copy result into register
		sta 	Reg16
		lda 	temp1+1
		sta 	Reg16+1
		jmp 	ExecLoop

ModulusHandler:	;; MOD $88
		jsr 	EvaluateValue 				; temp0 = target value.
		lda 	Reg16 						; temp1 = reg16
		sta 	temp1
		lda	 	Reg16+1
		sta 	temp1+1
		jsr 	Divide 						; temp1 := temp1 / temp0, mod => Reg16
		jmp 	ExecLoop

; *******************************************************************************************
;
;							temp1 := temp1 / temp0, mod in Reg16
;
; *******************************************************************************************

;
;	temp1 = Q temp0 = M Reg16 = A
;
Divide:
		lda 	#0 							; set A = 0
		sta 	Reg16
		sta 	Reg16+1
		ldy 	#16 						; loop round 16 times.
_DivLoop:
		asl 	temp1 						; shift QA left. Q first
		rol 	temp1+1
		;
		rol 	Reg16 						; shift A left carrying in.
		rol 	Reg16+1		
		;
		sec 								; calculate A-M, result in XA/C
		lda 	Reg16
		sbc 	temp0
		tax
		lda 	Reg16+1
		sbc 	temp0+1
		bcc 	_DivNoUpdate 				; if A >= M then store result and set Q bit 0.
		;
		sta 	Reg16+1
		stx 	Reg16
		inc 	temp1 						; we know it is even.
		;
_DivNoUpdate:		
		dey
		bne 	_DivLoop
		rts
