; *******************************************************************************************
; *******************************************************************************************
;
;       File:           asm6502.asm
;       Date:           13th November 2020
;       Purpose:        AMORAL Runtime outer shell.
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

		.include 	"macros.asm"

; *******************************************************************************************
;
;									  Runtime setup
;
; *******************************************************************************************

RunTimeAddress = $1000 						; Runtime loads at this address (e.g. Boot)
VariableMemory = $C00 						; Variable memory here (128 per 1/4k) PAGE BOUNDARY.
ZeroPageBase = $08 							; Zero page goes here.

; *******************************************************************************************
;
;									Zero Page Usage
;
; *******************************************************************************************

Reg16 = ZeroPageBase 						; the current value register.
Pctr = ZeroPageBase+2 						; the program counter (e.g. the next instruction)
temp0 = ZeroPageBase+4 						; temporary registers

; *******************************************************************************************
;
;										Boot Area
;
; *******************************************************************************************

		* =	RunTimeAddress
		lda 	#$60
		ldx 	#$4A
		jsr 	RunPCode
		.byte 	$90,$3C,$57
		.byte 	$BA,$02,$01
		.byte 	$80,$FE
		.byte 	$CA,$80,$08
		.byte 	$B0,$02,$01
		.byte 	$C0,$80,$08
		.byte 	$89

		* = 	RunTimeAddress+26			; the setup area
		.word 	RunTimeAddress 				; the address of boot
		.word	RunTimeEnd 					; where the runtime ends (e.g. where code goes)
		.word 	$0000 						; address of allocatable memory (set up by compiler)

		.include "interpreter.asm" 			; main interpreter
		.include "commands.asm"				; command handlers.
		.include "support.asm"				; support for command handlers

EndRunPCode:

RuntimeEnd:		
		.word 	0 							; end marker for dictionary.

