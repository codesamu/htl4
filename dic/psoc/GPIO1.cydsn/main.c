#include "project.h"

void clear(){
    LED_5_Write(0);
    LED_1_Write(0);
    LED_3_Write(0);
    LED_7_Write(0);
    LED_4_Write(0);
    LED_2_Write(0);
    LED_6_Write(0);
}

void one(){
    clear();
    LED_4_Write(1);
}

void two(){
    clear();
    LED_5_Write(1);
    LED_1_Write(1);
}

void three(){
    clear();
    LED_5_Write(1);
    LED_1_Write(1);
    LED_4_Write(1);
}

void four(){
    clear();
    LED_5_Write(1);
    LED_1_Write(1);
    LED_3_Write(1);
    LED_7_Write(1);
}

void five(){
    clear();
    LED_5_Write(1);
    LED_1_Write(1);
    LED_3_Write(1);
    LED_7_Write(1);
    LED_4_Write(1);
}

void six(){
    clear();
    LED_5_Write(1);
    LED_1_Write(1);
    LED_3_Write(1);
    LED_7_Write(1);
    LED_2_Write(1);
    LED_6_Write(1);
    
}

int main(void)
{
    CyGlobalIntEnable; /* Enable global interrupts. */

    uint8_t step = 0;

    for(;;)
    {
        if (Taster_Read() == 0) {
            switch(step) {
                case 0:
                    one();
                    break;
                case 1:
                    two();
                    break;
                case 2:
                    three();
                    break;
                case 3:
                    four();
                    break;
                case 4:
                    five();
                    break;
                case 5:
                    six();
                    break;
                default:
                    clear();
                    break;
            }

            step++;
            if (step > 6) step = 0; // Reset after the last step
            CyDelay(250);
        } else {
            // Wait for button press
            while(Taster_Read() != 0);
        }
    }
}




// int main(void)
// {
//     CyGlobalIntEnable; /* Enable global interrupts. */
//
//     for(;;)
//     {
//         if (Taster_Read() == 0) {
//             one();
//             CyDelay(250);
//         } else {
//             for(;;){if (Taster_Read() == 0){main();}}
//         }
//         
//         if (Taster_Read() == 0) {
//             two();
//             CyDelay(250);
//         } else {
//             for(;;){if (Taster_Read() == 0){main();}}
//         }
//         if (Taster_Read() == 0) {
//             three();
//             CyDelay(250);
//         } else {
//             for(;;){if (Taster_Read() == 0){main();}}
//         }
//         if (Taster_Read() == 0) {
//             four();
//             CyDelay(250);
//         } else {
//             for(;;){if (Taster_Read() == 0){main();}}
//         }
//         if (Taster_Read() == 0) {
//             five();
//             CyDelay(250);
//         } else {
//             for(;;){if (Taster_Read() == 0){main();}}
//         }
//         if (Taster_Read() == 0) {
//             six();
//             CyDelay(250);
//         } else {
//             for(;;){if (Taster_Read() == 0){main();}}
//         }
//         if (Taster_Read() == 0) {
//             clear();
//             CyDelay(250);
//             
//         } else {
//             for(;;){if (Taster_Read() == 0){main();}}
//             
//         }
//     }
// }

/* [] END OF FILE */
