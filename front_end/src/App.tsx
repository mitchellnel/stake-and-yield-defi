import React from 'react';
import { ChainId, DAppProvider } from '@usedapp/core';
import { Container } from "@material-ui/core"

import { Header } from "./components/Header"
import { Main } from "./components/Main"

function App() {
    return (
        <DAppProvider config={{
            supportedChains: [ChainId.Rinkeby]
        }}>
            <Header />
            <Container maxWidth="md">
                <div><h1>Poggers.</h1></div>
                <Main />
            </Container>
        </DAppProvider>
    );
}

export default App;
