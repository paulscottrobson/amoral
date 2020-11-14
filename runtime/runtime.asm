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
		.if test==1
		jmp 	TestRuntimeCode
		.else
		jmp 	RunTimeAddress
		.endif

		* = 	RunTimeAddress+26			; the setup area
		.word 	RunTimeAddress 				; the address of boot
		.word	RunTimeEnd 					; where the runtime ends (e.g. where code goes)
		.word 	$0000 						; address of allocatable memory (set up by compiler)

		.include "interpreter.asm" 			; main interpreter
		.include "commands.asm"				; command handlers.
		.include "support.asm"				; support for command handlers


		.if test==1 						; include test code if needed.			
TestRuntimeCode:
		ldx 	#$AB 						; something to work with
		lda 	#$CD
		jsr 	RunPCode 					; go do the following code.	
		.include "generated/testasm.inc"
		debug
		.endif

EndRunPCode:

RuntimeEnd:		
		.word 	0 							; end marker for dictionary.

