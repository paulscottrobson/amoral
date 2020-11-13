; *******************************************************************************************
; *******************************************************************************************
;
;       File:           interpreter.asm
;       Date:           13th November 2020
;       Purpose:        Main interpreter
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;		Run PCode following the call. Note that on entry XA contains the accumulator
;
; *******************************************************************************************

		define	"runpcode",EndRunPCode
RunPCode:
		stx 	Reg16+1 					; save the current XA values.
		sta 	Reg16

		pla 								; pull the address into the PC
		sta 	Pctr
		pla
		sta 	Pctr+1 

		inc16 	Pctr						; it is one short because RTS pops and increments.

; *******************************************************************************************
;
;								This is the main execution loop
;
; *******************************************************************************************

ExecLoop:
		ldy 	#0							; get the next instruction
		lda 	(Pctr),y
		inc16 	Pctr 						; advance the program pointer
		asl 	a 							; shift bit 7 into carry.
		bcs 	CommandHandler 				; 80-FF it's a command

; *******************************************************************************************
;
;		00-7F, call a routine. A contains the instruction x 2, the LSB to call
;
; *******************************************************************************************

		sta 	temp0 						; construct the call address in temp0
		lda 	(PCtr),y 					; get the MSB
		sta 	temp0+1
		inc16 	Pctr 						; advance the PCTR

		lda 	Pctr 						; save PCTR on 6502 stack
		pha
		lda 	Pctr+1
		pha

		lda 	Reg16 						; restore Reg16 into XA
		ldx 	Reg16+1

		jsr 	CallTemp0 					; call the routine as 6502 code.

		stx 	Reg16+1 					; save Reg16 back
		sta 	Reg16

		pla 								; restore the program counter
		sta 	Pctr+1
		pla
		sta 	Pctr

		jmp 	ExecLoop 					; and go round again.

CallTemp0:
		jmp 	(temp0)

; *******************************************************************************************
;
;								Handle instruction 80-FF
;
; *******************************************************************************************

CommandHandler:		
		ror 	a 							; patch it back so it has the full opcode.
		tay  								; save it in Y for use by the commands.
		cmp 	#$F0 						; is it a unary operation.
		bcs 	_CHIsUnary
		and 	#$0F 						; get the command number out.
		jmp 	_CHCall 					; go do the call
		;
_CHIsUnary:
		and 	#$0F 						; this is the unary command number		
		ora 	#$10 						; mapped onto $10-$1F
		;
_CHCall:									; at this point $00-$0F for non unary, $10-$1F for unary
		debug
		asl 	a 							; now offset in the jump table and into X
		tax
		lda 	JumpTable,x 				; copy the jump table vectors into temp0
		sta 	temp0
		lda 	JumpTable+1,x
		sta 	temp0+1
		jmp 	(temp0)						; and go there to execute with the opcode in Y.

OpcodeError: 								; come here if not found.
		debug 

;
;		The instruction table, which is produced by scanning the source code for markers.
;
JumpTable:		
		.include "generated/jumptable.inc"	