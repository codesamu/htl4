/*******************************************************************************
* File Name: Taster.h  
* Version 2.20
*
* Description:
*  This file contains Pin function prototypes and register defines
*
* Note:
*
********************************************************************************
* Copyright 2008-2015, Cypress Semiconductor Corporation.  All rights reserved.
* You may use this file only in accordance with the license, terms, conditions, 
* disclaimers, and limitations in the end user license agreement accompanying 
* the software package with which this file was provided.
*******************************************************************************/

#if !defined(CY_PINS_Taster_H) /* Pins Taster_H */
#define CY_PINS_Taster_H

#include "cytypes.h"
#include "cyfitter.h"
#include "cypins.h"
#include "Taster_aliases.h"

/* APIs are not generated for P15[7:6] */
#if !(CY_PSOC5A &&\
	 Taster__PORT == 15 && ((Taster__MASK & 0xC0) != 0))


/***************************************
*        Function Prototypes             
***************************************/    

/**
* \addtogroup group_general
* @{
*/
void    Taster_Write(uint8 value);
void    Taster_SetDriveMode(uint8 mode);
uint8   Taster_ReadDataReg(void);
uint8   Taster_Read(void);
void    Taster_SetInterruptMode(uint16 position, uint16 mode);
uint8   Taster_ClearInterrupt(void);
/** @} general */

/***************************************
*           API Constants        
***************************************/
/**
* \addtogroup group_constants
* @{
*/
    /** \addtogroup driveMode Drive mode constants
     * \brief Constants to be passed as "mode" parameter in the Taster_SetDriveMode() function.
     *  @{
     */
        #define Taster_DM_ALG_HIZ         PIN_DM_ALG_HIZ
        #define Taster_DM_DIG_HIZ         PIN_DM_DIG_HIZ
        #define Taster_DM_RES_UP          PIN_DM_RES_UP
        #define Taster_DM_RES_DWN         PIN_DM_RES_DWN
        #define Taster_DM_OD_LO           PIN_DM_OD_LO
        #define Taster_DM_OD_HI           PIN_DM_OD_HI
        #define Taster_DM_STRONG          PIN_DM_STRONG
        #define Taster_DM_RES_UPDWN       PIN_DM_RES_UPDWN
    /** @} driveMode */
/** @} group_constants */
    
/* Digital Port Constants */
#define Taster_MASK               Taster__MASK
#define Taster_SHIFT              Taster__SHIFT
#define Taster_WIDTH              1u

/* Interrupt constants */
#if defined(Taster__INTSTAT)
/**
* \addtogroup group_constants
* @{
*/
    /** \addtogroup intrMode Interrupt constants
     * \brief Constants to be passed as "mode" parameter in Taster_SetInterruptMode() function.
     *  @{
     */
        #define Taster_INTR_NONE      (uint16)(0x0000u)
        #define Taster_INTR_RISING    (uint16)(0x0001u)
        #define Taster_INTR_FALLING   (uint16)(0x0002u)
        #define Taster_INTR_BOTH      (uint16)(0x0003u) 
    /** @} intrMode */
/** @} group_constants */

    #define Taster_INTR_MASK      (0x01u) 
#endif /* (Taster__INTSTAT) */


/***************************************
*             Registers        
***************************************/

/* Main Port Registers */
/* Pin State */
#define Taster_PS                     (* (reg8 *) Taster__PS)
/* Data Register */
#define Taster_DR                     (* (reg8 *) Taster__DR)
/* Port Number */
#define Taster_PRT_NUM                (* (reg8 *) Taster__PRT) 
/* Connect to Analog Globals */                                                  
#define Taster_AG                     (* (reg8 *) Taster__AG)                       
/* Analog MUX bux enable */
#define Taster_AMUX                   (* (reg8 *) Taster__AMUX) 
/* Bidirectional Enable */                                                        
#define Taster_BIE                    (* (reg8 *) Taster__BIE)
/* Bit-mask for Aliased Register Access */
#define Taster_BIT_MASK               (* (reg8 *) Taster__BIT_MASK)
/* Bypass Enable */
#define Taster_BYP                    (* (reg8 *) Taster__BYP)
/* Port wide control signals */                                                   
#define Taster_CTL                    (* (reg8 *) Taster__CTL)
/* Drive Modes */
#define Taster_DM0                    (* (reg8 *) Taster__DM0) 
#define Taster_DM1                    (* (reg8 *) Taster__DM1)
#define Taster_DM2                    (* (reg8 *) Taster__DM2) 
/* Input Buffer Disable Override */
#define Taster_INP_DIS                (* (reg8 *) Taster__INP_DIS)
/* LCD Common or Segment Drive */
#define Taster_LCD_COM_SEG            (* (reg8 *) Taster__LCD_COM_SEG)
/* Enable Segment LCD */
#define Taster_LCD_EN                 (* (reg8 *) Taster__LCD_EN)
/* Slew Rate Control */
#define Taster_SLW                    (* (reg8 *) Taster__SLW)

/* DSI Port Registers */
/* Global DSI Select Register */
#define Taster_PRTDSI__CAPS_SEL       (* (reg8 *) Taster__PRTDSI__CAPS_SEL) 
/* Double Sync Enable */
#define Taster_PRTDSI__DBL_SYNC_IN    (* (reg8 *) Taster__PRTDSI__DBL_SYNC_IN) 
/* Output Enable Select Drive Strength */
#define Taster_PRTDSI__OE_SEL0        (* (reg8 *) Taster__PRTDSI__OE_SEL0) 
#define Taster_PRTDSI__OE_SEL1        (* (reg8 *) Taster__PRTDSI__OE_SEL1) 
/* Port Pin Output Select Registers */
#define Taster_PRTDSI__OUT_SEL0       (* (reg8 *) Taster__PRTDSI__OUT_SEL0) 
#define Taster_PRTDSI__OUT_SEL1       (* (reg8 *) Taster__PRTDSI__OUT_SEL1) 
/* Sync Output Enable Registers */
#define Taster_PRTDSI__SYNC_OUT       (* (reg8 *) Taster__PRTDSI__SYNC_OUT) 

/* SIO registers */
#if defined(Taster__SIO_CFG)
    #define Taster_SIO_HYST_EN        (* (reg8 *) Taster__SIO_HYST_EN)
    #define Taster_SIO_REG_HIFREQ     (* (reg8 *) Taster__SIO_REG_HIFREQ)
    #define Taster_SIO_CFG            (* (reg8 *) Taster__SIO_CFG)
    #define Taster_SIO_DIFF           (* (reg8 *) Taster__SIO_DIFF)
#endif /* (Taster__SIO_CFG) */

/* Interrupt Registers */
#if defined(Taster__INTSTAT)
    #define Taster_INTSTAT            (* (reg8 *) Taster__INTSTAT)
    #define Taster_SNAP               (* (reg8 *) Taster__SNAP)
    
	#define Taster_0_INTTYPE_REG 		(* (reg8 *) Taster__0__INTTYPE)
#endif /* (Taster__INTSTAT) */

#endif /* CY_PSOC5A... */

#endif /*  CY_PINS_Taster_H */


/* [] END OF FILE */
