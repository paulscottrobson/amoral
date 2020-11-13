; *******************************************************************************************
; *******************************************************************************************
;
;       File:           macros.asm
;       Date:           13th November 2020
;       Purpose:        AMORAL Macros
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;									Break into debugger
;
; *******************************************************************************************

debug .macro
	.byte 	$DB
	.endm


; *******************************************************************************************
;
;							  Define a new word in the runtime
;
; *******************************************************************************************

define .macro
	.word 	\2-* 							; offset to next entry
	.text 	\1,0 							; the text (must be lower case)
	.align 	2								; force to even boundary.
	.endm

; *******************************************************************************************
;
;									16 bit utilities
;
; *******************************************************************************************

inc16 .macro
	inc 	\1
	bne 	nocarry
	inc 	1+(\1)
nocarry:
	.endm

dec16 .macro
	lda 	\1
	bne 	noborrow
	dec 	1+(\1)
.noborrow:
	dec 	\1
	.endm
	
	
