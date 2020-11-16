; *******************************************************************************************
; *******************************************************************************************
;
;       File:           utility.asm
;       Date:           14th November 2020
;       Purpose:        Utility routines for 6502 code.
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;									Clear variable space
;
; *******************************************************************************************

		define 	"clear.variables:0",EndVariableClear
VariableClear:
		lda 	#VarAddr & $FF
		sta 	temp0
		lda 	#VarAddr >> 8
		sta		temp0+1
		ldx 	#VarPages
		ldy 	#0
		tya
_VCLoop:sta 	(temp0),y
		iny
		bne 	_VCLoop
		inc 	temp0+1
		dex
		bne 	_VCLoop
		rts

EndVariableClear:

; *******************************************************************************************
;
;										Stop
;
; *******************************************************************************************

		define 	"halt.program:0",EndHaltProgram
HaltProgram:
		jmp 	HaltProgram
EndHaltProgram:

; *******************************************************************************************
;
;									Boot address
;
; *******************************************************************************************
		
		define "boot.address:0",EndBootAddress
		lda 	#BootAddr & $FF
		ldx 	#BootAddr >> 8
		rts
EndBootAddress:
; *******************************************************************************************
;
;								Print Hex w/leading space
;
; *******************************************************************************************

		define 	"print.hex:1",EndPrintHex
PrintHex:
		pha
		lda 	#32
		jsr 	PrintCharacter
		txa
		jsr 	_PHex
		pla
_PHex:	pha
		lsr 	a
		lsr 	a
		lsr 	a
		lsr 	a
		jsr 	_PNibl
		pla
_PNibl:	and 	#15
		cmp 	#10
		bcc 	_PNoSkip
		adc 	#6
_PNoSkip:
		adc 	#48
		jmp 	PrintCharacter						

EndPrintHex:

; *******************************************************************************************
;
;								Print ASCIIZ String
;
; *******************************************************************************************

		define 	"print.string:1",EndPrintString
PrintString:
		sta 	temp0
		stx 	temp0+1
		ldy 	#0
_PSLoop:lda 	(temp0),y
		beq 	_PSExit
		jsr 	PrintCharacter
		iny
		bne 	_PSLoop
_PSExit:rts		

EndPrintString

; *******************************************************************************************
;
;									Print Decimal/Signed
;
; *******************************************************************************************

		define "print.int:1",EndPrintDecimal
PrintDecimal:
		pha
		lda 	#32							; leading spaces.
		jsr 	PrintCharacter
		pla
PDEntry:		
		sta 	temp1						; save in temp1
		stx 	temp1+1
_PDRecurse:		
		lda 	#10 						; set base to 10.
		sta 	temp0
		lda 	#0
		sta 	temp0+1
		jsr 	Divide
		lda 	Reg16 						; push remainder on stack.
		pha
		lda 	temp1						; call recursively if not zero
		ora 	temp1+1
		beq 	_PDNoRecurse
		jsr 	_PDRecurse 					; recursively print
_PDNoRecurse:
		pla 								; restore and print 
		ora 	#48		
		jmp 	PrintCharacter
EndPrintDecimal:
		
		define "print.sint:1",EndPrintSignedInt
		cpx 	#0
		beq 	PrintDecimal
		pha
		lda 	#32
		jsr 	PrintCharacter
		lda 	#'-'
		jsr 	PrintCharacter
		pla
		jsr 	Negate
		jmp 	PDEntry
EndPrintSignedInt:

; *******************************************************************************************
;
;										Negate XA
;
; *******************************************************************************************

		define 	"neg:0",EndNegate
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
