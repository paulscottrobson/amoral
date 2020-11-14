; *******************************************************************************************
; *******************************************************************************************
;
;       File:           support.asm
;       Date:           13th November 2020
;       Purpose:        Command handlers EAC/Value calculation routines.
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

; *******************************************************************************************
;
;								Opcode in Y,Evaluate Data
;
; *******************************************************************************************

EvaluateValue:
		tya 								; get EAC part and save in X
		and 	#$70
		tax 					
		cmp 	#$20 						; check if 00,01 if so it is variable or absolute
		bcs 	_EDMemory
		;
		;	Immediate : <opcode> <low> or <opcode> <low> <high>
		;
		ldy 	#0 							; read first byte into temp0
		lda 	(Pctr),y
		sta 	temp0
		sty 	temp0+1 					; make it 16 bit.
		inc16 	Pctr
		cpx 	#0 							; if it is 000 then it is a one byte
		beq 	_EACalcValue
		lda 	(Pctr),y 					; read 2nd byte into temp0+1
		sta 	temp0+1
		inc16 	Pctr
_EACalcValue:
		rts
		;
		;	Either a variable offset (short/long) or an absolute address
		;
_EDMemory:
		jsr	 	EvaluateAddress 			; evaluate the address.
		;
		ldy 	#0 							; 16 bit load indirect (temp0) => temp0
		lda 	(temp0),y 			
		tax
		iny
		lda 	(temp0),y 			
		stx 	temp0
		sta 	temp0+1
		rts

; *******************************************************************************************
;
;			Opcode in Y, evaluate effective address of opcode (not immediates)
;
; *******************************************************************************************

EvaluateAddress:		
		tya 								; get EAC part of opcode.
		and 	#$70
		cmp 	#$40 						; is it an absolute address
		beq 	_EAAbsolute
;
;		Variable address : <opcode> <low> or <opcode> <low> <high>
;
		tax 								; save in X
		ldy 	#0 							; read first byte into temp0
		lda 	(Pctr),y
		sta 	temp0
		sty 	temp0+1 					; make it 16 bit.
		inc16 	Pctr
		cpx 	#$20 						; if it is 010 then it is a one byte
		beq 	_EACalcVarAddress
		lda 	(Pctr),y 					; read 2nd byte into temp0+1
		sta 	temp0+1
		inc16 	Pctr
_EACalcVarAddress:
		asl 	temp0 						; double the variable number
		rol 	temp0+1
		clc 								; add the page address of variable data on.
		lda 	temp0+1
		adc 	#VarAddr/256 
		sta 	temp0+1
		rts
;
;		Absolute address : <opcode> <low> <high>
;
_EAAbsolute:
		ldy 	#0 							; get the address into temp0
		lda 	(Pctr),y 			
		sta 	temp0
		iny
		lda 	(Pctr),y 			
		sta 	temp0+1		
ReturnBump2									; bump pc by 2 and loop back
		inc16	Pctr
ReturnBump1:								; bump PC by 1 and loop back
		inc16 	Pctr		
		rts
