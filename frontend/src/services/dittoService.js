/**
 * Placeholder Ditto Service for Twin-Lite
 * No Ditto integration in lite version
 */

const dittoService = {
    // Placeholder methods that do nothing
    connect: async () => {
        console.warn('Ditto service not available in Twin-Lite');
        return false;
    },

    disconnect: () => {
        console.warn('Ditto service not available in Twin-Lite');
    },

    getThing: async () => {
        console.warn('Ditto service not available in Twin-Lite');
        return null;
    },

    createThing: async () => {
        console.warn('Ditto service not available in Twin-Lite');
        return null;
    },

    updateThing: async () => {
        console.warn('Ditto service not available in Twin-Lite');
        return null;
    },

    deleteThing: async () => {
        console.warn('Ditto service not available in Twin-Lite');
        return false;
    },
};

export default dittoService;
