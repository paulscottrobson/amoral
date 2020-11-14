; *******************************************************************************************
; *******************************************************************************************
;
;       File:           commands.asm
;       Date:           13th November 2020
;       Purpose:        Command handlers
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;									Handles load.
;
; *******************************************************************************************

LoadHandler:	;; LDR $80
		jsr 	EvaluateValue 				; temp0 = target value.
		lda 	temp0						; copy value into register
		sta 	Reg16
		lda 	temp0+1
		sta 	Reg16+1
		jmp 	ExecLoop

; *******************************************************************************************
;
;									Handles store
;
; *******************************************************************************************

StoreHandler: 	;; STR $8A
		jsr 	EvaluateAddress 			; temp0 = target address.
		ldy 	#0							; write register out
		lda 	Reg16 
		sta 	(temp0),y
		lda 	Reg16+1
		iny
		sta 	(temp0),y
		jmp 	ExecLoop

; *******************************************************************************************
;
;									Add and Subtract
;
; *******************************************************************************************

Addhandler: 	;; ADD $84
		jsr 	EvaluateValue
		clc
		lda 	Reg16
		adc 	temp0
		sta 	Reg16
		lda 	Reg16+1
		adc 	temp0+1
		sta 	Reg16+1
		jmp 	ExecLoop

Subhandler: 	;; SUB $85
		jsr 	EvaluateValue
		sec
		lda 	Reg16
		sbc 	temp0
		sta 	Reg16
		lda 	Reg16+1
		sbc 	temp0+1
		sta 	Reg16+1
		jmp 	ExecLoop

; *******************************************************************************************
;
;									Binary Operations
;
; *******************************************************************************************

Andhandler: 	;; AND $81
		jsr 	EvaluateValue
		lda 	Reg16
		and 	temp0
		sta 	Reg16
		lda 	Reg16+1
		and 	temp0+1
		sta 	Reg16+1
		jmp 	ExecLoop

Orhandler: 		;; ORR $82
		jsr 	EvaluateValue
		lda 	Reg16
		ora 	temp0
		sta 	Reg16
		lda 	Reg16+1
		ora 	temp0+1
		sta 	Reg16+1
		jmp 	ExecLoop

Xorhandler: 	;; XOR $83
		jsr 	EvaluateValue
		lda 	Reg16
		eor 	temp0
		sta 	Reg16
		lda 	Reg16+1
		eor 	temp0+1
		sta 	Reg16+1
		jmp 	ExecLoop
