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
;									Print Character
;
; *******************************************************************************************

		define 	"print.character",EndPrintCharacter
PrintCharacter:
		jsr 	$FFD2
		rts

EndPrintCharacter:

; *******************************************************************************************
;
;								Print Hex w/leading space
;
; *******************************************************************************************

		define 	"print.hex",EndPrintHex
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

		define 	"print.string",EndPrintString
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