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

.weak

BootAddr = $1000 							; Runtime loads at this address (e.g. Boot)

VarAddr = $800 								; Variable memory here (128 per 1/4k) PAGE BOUNDARY.

ZeroAddr = $08 								; Zero page goes here.

test = 0									; test to run (default is build final)

.endweak

; *******************************************************************************************
;
;									Zero Page Usage
;
; *******************************************************************************************

Reg16 = ZeroAddr 							; the current value register.
Pctr = ZeroAddr+2 							; the program counter (e.g. the next instruction)
temp0 = ZeroAddr+4 							; temporary registers
temp1 = ZeroAddr+6

; *******************************************************************************************
;
;										Boot Area
;
; *******************************************************************************************

		* =	BootAddr
		.if test==1
		jmp 	TestRuntimeCode 			; test=1 runs code build with rasm.py
		.endif
		.if test==2 						; test=2 tests the externally callable functions
		jmp 	TestExternal
		.endif
		
		jmp 	BootAddr 					; test=0 what we normally get, no start address.

		* = 	BootAddr+24					; the setup area
		.word 	BootAddr 					; the address of boot
		.word 	VarAddr 					; the address of the variables
		.word	RunTimeEnd 					; where the runtime ends (e.g. where code goes)
		.word 	$0000 						; address of allocatable memory (set up by compiler)

; *******************************************************************************************
;
;		The first word "runpcode" encompasses the interpreter and all its support functions.
;
; *******************************************************************************************

		define	"runpcode",EndRunPCode

		.include "interpreter.asm" 			; main interpreter

		.include "commands.asm"				; command handlers.
		.include "support.asm"				; support for command handlers
		.include "branches.asm"				; branch handlers
		.include "unary.asm"				; unary handlers	
		.include "multiply.asm"				; multiply code.
		.include "divide.asm"				; divide/modulus code.
		
		.if test==1 						; include test code if needed.			
TestRuntimeCode:
		ldx 	#$AB 						; something to work with
		lda 	#$CD
		jsr 	RunPCode 					; go do the following code.	
		.include "generated/testasm.inc"
		debug
		.endif

EndRunPCode:

; *******************************************************************************************
;
;		Other words. Their words should be self contained and maintain the linked list.
;
; *******************************************************************************************

RuntimeEnd:		
		.include 	"muldiv.asm"			; routines that provide support for 6502 code mul and div.
		.include 	"utility.asm"			; utility functions.
;
;		As is, there is no end marker, so that code can be added on.
;

