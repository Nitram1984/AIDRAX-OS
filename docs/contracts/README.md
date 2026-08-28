# CA-013 Contract Classification

Die CA-013-Verträge verwenden genau diese Stabilitätsklassen:

| Klasse | Bedeutung |
|---|---|
| **Public** | Versionierter, kompatibilitätsgeschützter Aufruf- oder Kommandovertrag. |
| **Internal** | Implementierungsdetail ohne Kompatibilitätszusage. |
| **Experimental** | Kein CA-013-API-Element trägt diese Klasse. Künftige experimentelle Oberflächen benötigen eine ausdrückliche Kennzeichnung. |
| **Deprecated** | Kein CA-013-API-Element ist deprecated. Eine spätere Ablösung benötigt eine Übergangsfrist und eine dokumentierte Ersatzschnittstelle. |

`CapabilityContract` definiert ab CA-015 den providerneutralen Capability-Lifecycle. `ProviderContract` bleibt ein öffentlicher Grenzvertrag ohne Providerintegration; die Runtime lädt weder Provider noch Plugins und benötigt keine Provider-Credentials.
