; *******************************************************************************************
; *******************************************************************************************
;
;       File:           utility3.asm
;       Date:           16th November 2020
;       Purpose:        More Utility routines for 6502 code.
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;										Peek.word/byte
;
; *******************************************************************************************

		define 	"peek.b:1",EndPeekB
		sta 	temp0
		stx 	temp0+1
		ldy 	#0
		lda 	(temp0),y
		ldx 	#0
		rts
EndPeekB:

		define 	"peek.w:1",EndPeekW
		sta 	temp0
		stx 	temp0+1
		ldy 	#1
		lda 	(temp0),y
		tax
		dey
		lda 	(temp0),y
		rts
EndPeekW:

; *******************************************************************************************
;
;										Poke.word/byte
;
; *******************************************************************************************

		define 	"poke.b:2",EndPokeB
		ldy 	Param1
		sty 	temp0
		ldy 	Param1+1
		sty 	temp0+1
		ldy 	#0
		sta 	(temp0),y
		rts
EndPokeB:

		define 	"poke.w:2",EndPokeW
		pha
		ldy 	Param1
		sty 	temp0
		ldy 	Param1+1
		sty 	temp0+1
		ldy 	#0
		sta 	(temp0),y
		iny
		txa
		sta 	(temp0),y
		pla
		rts
EndPokeW:
